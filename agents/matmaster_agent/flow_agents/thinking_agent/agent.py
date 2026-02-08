import logging
from typing import Any, AsyncGenerator, Optional, override

from google.adk.agents import InvocationContext
from google.adk.events import Event
from google.genai.types import Content, Part

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.core_agents.comp_agents.dntransfer_climit_agent import (
    DisallowTransferAndContentLimitLlmAgent,
)
from agents.matmaster_agent.flow_agents.thinking_agent.constant import (
    FIRST_ROUND_NEED_REVISION,
    FIRST_ROUND_READY,
    MAX_THINKING_ROUNDS,
    REVISION_OK,
    REVISION_OK_USER_MESSAGE,
)
from agents.matmaster_agent.flow_agents.thinking_agent.prompt import (
    get_dynamic_revision_user_block,
    get_dynamic_user_block,
    get_static_revision_system_block,
    get_static_system_block,
)
from agents.matmaster_agent.logger import PrefixFilter

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


def _collect_text_from_event(event: Event) -> str:
    if getattr(event, 'partial', True) or not getattr(event, 'content', None):
        return ''
    parts = getattr(event.content, 'parts', None) or []
    return ''.join(
        getattr(p, 'text', None) or ''
        for p in parts
        if getattr(p, 'text', None) is not None
    ).strip()


def _last_line(s: str) -> str:
    """Last non-empty line, stripped."""
    lines = [ln.strip() for ln in s.strip().splitlines() if ln.strip()]
    return lines[-1] if lines else ''


def _strip_first_round_marker(text: str) -> str:
    """Remove trailing READY. or Revision needed. line so downstream only sees reasoning."""
    if not text:
        return text
    lines = text.strip().splitlines()
    while lines:
        last = lines[-1].strip().upper()
        if (
            last == FIRST_ROUND_READY.upper()
            or last == FIRST_ROUND_NEED_REVISION.upper()
        ):
            lines.pop()
            continue
        break
    return '\n'.join(lines).strip()


def _model_wants_revision(thinking_text: str) -> bool:
    """True iff the model ended with Revision needed. (model decides, no hardcoded hints)."""
    return _last_line(thinking_text).upper() == FIRST_ROUND_NEED_REVISION.upper()


class ThinkingAgent(DisallowTransferAndContentLimitLlmAgent):
    """Agent that produces structured CoT reasoning (analysis → drafting → simulation → plan).
    When _thinking_params is set, runs an internal loop: planning round then verification;
    if not READY, keep revising until READY or max rounds (MAX_THINKING_ROUNDS).
    Uses static (system) vs dynamic (user) prompt separation for prompt caching.
    """

    _thinking_params: Optional[dict[str, Any]] = None

    def set_thinking_params(
        self,
        available_tools_with_info: str,
        session_file_summary: str,
        original_query: str,
        expanded_query: str,
        short_term_memory: str = '',
    ) -> None:
        """Set params for self-contained loop mode. Cleared after run_async."""
        self._thinking_params = {
            'available_tools_with_info': available_tools_with_info,
            'session_file_summary': session_file_summary,
            'original_query': original_query,
            'expanded_query': expanded_query,
            'short_term_memory': short_term_memory or '',
        }

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        params = self._thinking_params
        if params is None:
            async for event in super()._run_events(ctx):
                yield event
            return

        try:
            # Reuse tools string for cache key stability (generated once by flow, passed here)
            tools_str: str = params['available_tools_with_info']

            # Round 1: planning — set system (static) once, user (dynamic) this turn
            self.global_instruction = get_static_system_block(tools_str)
            self.instruction = get_dynamic_user_block(
                params['session_file_summary'],
                params['original_query'],
                params['expanded_query'],
                params.get('short_term_memory', ''),
            )
            last_full_text = ''
            round1_events: list[Event] = []
            async for event in super()._run_events(ctx):
                round1_events.append(event)
                t = _collect_text_from_event(event)
                if t:
                    last_full_text = t
            thinking_text = last_full_text.strip()
            # Do not show "Revision needed." to user — it is an internal protocol; user only sees reasoning, then later "校验通过，采用当前规划。"
            stripped_round1 = _strip_first_round_marker(thinking_text)
            if stripped_round1 != thinking_text and round1_events:
                for i in range(len(round1_events) - 1, -1, -1):
                    ev = round1_events[i]
                    if getattr(ev, 'content', None) and getattr(
                        ev.content, 'parts', None
                    ):
                        for j, p in enumerate(ev.content.parts):
                            if getattr(p, 'text', None) is not None:
                                new_parts = list(ev.content.parts)
                                new_parts[j] = Part(text=stripped_round1)
                                round1_events[i] = Event(
                                    author=getattr(ev, 'author', self.name),
                                    invocation_id=getattr(
                                        ev, 'invocation_id', ctx.invocation_id
                                    ),
                                    content=Content(
                                        parts=new_parts,
                                        role=getattr(ev.content, 'role', 'model'),
                                    ),
                                    partial=getattr(ev, 'partial', True),
                                )
                                break
                    break
            for ev in round1_events:
                yield ev
            round_index = 1

            # Rounds 2..MAX: set revision system (static) once, user (dynamic) every turn
            self.global_instruction = get_static_revision_system_block(tools_str)
            while round_index < MAX_THINKING_ROUNDS:
                previous_reasoning = _strip_first_round_marker(thinking_text)
                self.instruction = get_dynamic_revision_user_block(
                    params['session_file_summary'],
                    params['original_query'],
                    params['expanded_query'],
                    previous_reasoning=previous_reasoning,
                    short_term_memory=params.get('short_term_memory', ''),
                )
                last_full_text = ''
                revision_events: list[Event] = []
                async for event in super()._run_events(ctx):
                    revision_events.append(event)
                    t = _collect_text_from_event(event)
                    if t:
                        last_full_text = (last_full_text + t) if last_full_text else t
                round_text = last_full_text.strip()
                round_index += 1

                # Verification passed = model concluded with "Verification passed." or "OK" (last line); match leniently to avoid loop when model varies punctuation/case
                _last = _last_line(round_text).strip().upper()
                last_line_ok = (
                    _last == REVISION_OK.upper()
                    or _last == 'OK'
                    or _last.rstrip('.').endswith('VERIFICATION PASSED')
                )
                if last_line_ok:
                    # Verification passed: keep current reasoning; always stream the verification round so user sees the process (must have planning + verification visible)
                    thinking_text = previous_reasoning or thinking_text
                    # If model only output that one line (no verification process), replace last event text with human-friendly message; otherwise stream as-is
                    _lines = [
                        ln for ln in round_text.strip().splitlines() if ln.strip()
                    ]
                    only_final_line = len(_lines) <= 1 and (
                        _last == REVISION_OK.upper()
                        or _last == 'OK'
                        or _last.rstrip('.').endswith('VERIFICATION PASSED')
                    )
                    if only_final_line:
                        for i in range(len(revision_events) - 1, -1, -1):
                            ev = revision_events[i]
                            if getattr(ev, 'content', None) and getattr(
                                ev.content, 'parts', None
                            ):
                                for j, p in enumerate(ev.content.parts):
                                    if getattr(p, 'text', None) is not None:
                                        new_parts = list(ev.content.parts)
                                        new_parts[j] = Part(
                                            text=REVISION_OK_USER_MESSAGE
                                        )
                                        revision_events[i] = Event(
                                            author=getattr(ev, 'author', self.name),
                                            invocation_id=getattr(
                                                ev, 'invocation_id', ctx.invocation_id
                                            ),
                                            content=Content(
                                                parts=new_parts,
                                                role=getattr(
                                                    ev.content, 'role', 'model'
                                                ),
                                            ),
                                            partial=getattr(ev, 'partial', True),
                                        )
                                        break
                            break
                    for ev in revision_events:
                        yield ev
                    break
                # Validation found errors: next round MUST be validation again until PASS. Use corrected output as input for next round.
                thinking_text = _strip_first_round_marker(round_text)
                for ev in revision_events:
                    yield ev

            # Downstream gets reasoning only (no READY./Revision needed. marker)
            self._last_thinking_text = _strip_first_round_marker(thinking_text)
        except Exception:
            self._last_thinking_text = None
            raise
        finally:
            self._thinking_params = None
