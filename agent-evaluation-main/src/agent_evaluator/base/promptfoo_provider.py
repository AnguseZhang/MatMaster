"""
Promptfoo Python provider for MatMaster ADK agent.

This module adapts Promptfoo's `call_api(prompt, options, context)` interface to the
MatMaster agent runtime (Google ADK Runner).
"""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List

import asyncio
from dotenv import find_dotenv, load_dotenv
from google.adk import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from agents.matmaster_agent.agent import root_agent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.utils.event_utils import is_function_call


def _load_env() -> None:
    """Load .env for local execution (idempotent)."""

    load_dotenv(find_dotenv(), override=True)


def _extract_user_messages(prompt: str) -> List[str]:
    """
    Extract user messages from Promptfoo prompt input.

    Promptfoo may pass either a plain string or a JSON-encoded chat thread:
    - String: "hello"
    - JSON list: [{"role":"user","content":"..."}, ...]
    """

    if not isinstance(prompt, str) or not prompt.strip():
        return []

    try:
        data = json.loads(prompt)
    except Exception:
        return [prompt]

    if isinstance(data, list):
        user_messages: List[str] = []
        for msg in data:
            if not isinstance(msg, dict):
                continue
            if msg.get("role") != "user":
                continue
            content = msg.get("content")
            if isinstance(content, str) and content.strip():
                user_messages.append(content)
        return user_messages

    return [prompt]


def _run_agent_once(
    *,
    runner: Runner,
    user_id: str,
    session_id: str,
    user_text: str,
    should_capture_function_call: bool,
) -> Dict[str, Any]:
    """Run a single user turn and return extracted output and function call (if any)."""

    content = genai_types.Content(role="user", parts=[genai_types.Part(text=user_text)])

    events: List[Any] = []
    function_call: Dict[str, Any] = {}

    for event in runner.run(user_id=user_id, session_id=session_id, new_message=content):
        events.append(event)
        if should_capture_function_call and is_function_call(event):
            function_call = {
                "function_name": event.content.parts[0].function_call.name,
                "function_args": event.content.parts[0].function_call.args,
            }
            break

    output_text = ""
    if events and events[-1].content and events[-1].content.parts:
        output_text = events[-1].content.parts[0].text or ""

    return {"output_text": output_text, "function_call": function_call}


def call_api(prompt: str, options: dict, context: dict) -> dict:
    """
    Promptfoo provider entrypoint.

    Args:
        prompt: Final prompt string or a JSON-encoded chat thread.
        options: Provider configuration from YAML.
        context: Variables and metadata for the current test.

    Returns:
        Dict with at least {"output": "..."} as required by Promptfoo.
    """

    _load_env()

    config = (options or {}).get("config", {}) or {}
    should_capture_function_call = bool(config.get("capture_function_call", True))
    should_annotate_output = bool(config.get("annotate_output_json", False))

    user_messages = _extract_user_messages(prompt)
    if not user_messages:
        return {"output": "", "error": "Empty prompt"}

    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    runner = Runner(
        agent=root_agent,
        app_name=MATMASTER_AGENT_NAME,
        session_service=session_service,
        artifact_service=artifact_service,
    )

    user_id = "promptfoo"
    try:
        # ADK requires session to exist in the session service.
        session = asyncio.run(
            session_service.create_session(
                app_name=MATMASTER_AGENT_NAME,
                user_id=user_id,
                session_id=uuid.uuid4().hex,
            )
        )

        last_result: Dict[str, Any] = {"output_text": "", "function_call": {}}
        for user_text in user_messages:
            last_result = _run_agent_once(
                runner=runner,
                user_id=user_id,
                session_id=session.id,
                user_text=user_text,
                should_capture_function_call=should_capture_function_call,
            )

        output_text = last_result["output_text"]
        function_call = last_result["function_call"]

        if should_annotate_output:
            return {
                "output": json.dumps(
                    {"text": output_text, "function_call": function_call},
                    ensure_ascii=False,
                )
            }

        response: Dict[str, Any] = {"output": output_text}
        if function_call:
            response["function_call"] = function_call
        return response
    finally:
        closed = runner.close()
        if hasattr(closed, "__await__"):
            asyncio.run(closed)


