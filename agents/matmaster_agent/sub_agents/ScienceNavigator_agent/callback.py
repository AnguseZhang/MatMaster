import json
import logging
import re


from google.adk.tools import ToolContext
from mcp.types import CallToolResult, TextContent

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import PrefixFilter

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)

DISCARD_KEYS = [
    'paperId',
    'publicationId',
    'publicationCover',
    'zhName',
    'zhAbstract',
    'languageType',
    'popularity',
    'goodFlag',
    'readFlag',
    'addFlag',
    'graphicalAbstract',
    'openAccess',
    'pdfFlag',
    'title',
    'authorDetails',
    'alltext',
]

MAX_ABSTRACT_LEN = 300
MIN_page_size = 150


def _process_web_search_response(tool_response):
    """
    Process web-search tool response by removing total_results field.
    """
    try:
        tool_output = tool_response.content
        output_json = json.loads(tool_output[0].text)

        # Remove total_results key if present
        if 'total_results' in output_json:
            del output_json['total_results']

        new_content = json.dumps(output_json)
        new_response = CallToolResult(
            content=[TextContent(type='text', text=new_content)],
            meta=getattr(tool_response, 'meta', None),
        )
        return new_response
    except Exception as e:
        logger.error(e)
        return tool_response


def _process_search_papers_enhanced_response(tool_response):
    """
    Process search-papers-enhanced tool response by filtering fields and truncating abstracts.
    """
    try:
        tool_output = tool_response.content
        output_json = json.loads(tool_output[0].text)
        output_paper_list = output_json['data']
    except Exception as e:
        logger.error(e)
        return tool_response

    filtered_papers = []
    for paper_info in output_paper_list:
        new_info = {k: v for k, v in paper_info.items() if k not in DISCARD_KEYS}
        # Clip Abstract field if it exceeds MAX_ABSTRACT_LEN
        if (
            'Abstract' in new_info
            and isinstance(new_info['Abstract'], str)
            and len(new_info['Abstract']) > MAX_ABSTRACT_LEN
        ):
            new_info['Abstract'] = new_info['Abstract'][:MAX_ABSTRACT_LEN] + '...'
        filtered_papers.append(new_info)

    new_content = json.dumps({'data': filtered_papers})
    new_response = CallToolResult(
        content=[TextContent(type='text', text=new_content)],
        meta=getattr(tool_response, 'meta', None),
    )

    return new_response


async def after_tool_callback(tool, args, tool_context, tool_response):
    logger.info(f"[after_tool_callback] Tool '{tool.name}' executed.")

    # Only process specific tools
    if tool.name == 'web-search':
        return _process_web_search_response(tool_response)
    elif tool.name == 'search-papers-enhanced':
        return _process_search_papers_enhanced_response(tool_response)
    else:
        # Return original response for unhandled tools
        return tool_response


def contains_chinese(text: str) -> bool:
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def translate_word_list_to_english(chinese_words: list) -> list:
    import litellm

    if not isinstance(chinese_words, list) or not chinese_words:
        return chinese_words

    # Only translate if at least one item contains Chinese
    if not any(isinstance(w, str) and contains_chinese(w) for w in chinese_words):
        return chinese_words  # no-op

    try:
        llm_config = LLMConfig()
        model = llm_config.gpt_5_nano.model

        # Build prompt: explicit JSON schema + few-shot example
        prompt = f"""
Translate the following list of search terms to English.
    - Preserve English terms, acronyms, numbers, and symbols exactly as they are.
    - Output ONLY a valid JSON list of strings. No explanations, no markdown, no prefix.
    - Example: ['密度', 'LAMMPS', 'ΔH'] → ['density', 'LAMMPS', 'ΔH']

Terms: {str(chinese_words)}
English translation (JSON list only):
"""

        response = litellm.completion(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
        )

        raw_output = response.choices[0].message.content.strip()

        # Try to extract JSON: handle common LLM hallucinations (e.g., ```json [...]```)
        # 1. Strip code fences
        if raw_output.startswith('```'):
            raw_output = re.split(r'```(?:json)?', raw_output, maxsplit=1)[-1]
            raw_output = raw_output.rsplit('```', 1)[0].strip()

        # 2. Try direct parse
        try:
            translated_list = json.loads(raw_output)
        except json.JSONDecodeError:
            # 3. Fallback: look for [...] in text
            match = re.search(r'\[.*\]', raw_output, re.DOTALL)
            if match:
                try:
                    translated_list = json.loads(match.group(0))
                except Exception:
                    raise ValueError('Failed to extract JSON from LLM output')
            else:
                raise ValueError('No JSON array found in LLM response')

        # Validate: must be list of strings, same length
        if not isinstance(translated_list, list) or len(translated_list) != len(
            chinese_words
        ):
            raise ValueError('Translated list length mismatch or invalid type')

        # Ensure all items are strings
        translated_list = [
            str(item).strip() if item is not None else '' for item in translated_list
        ]

        logger.info(f"[Batch translate] {chinese_words} → {translated_list}")
        return translated_list

    except Exception as e:
        logger.error(f"Batch translation failed for {chinese_words}: {e}")
        return chinese_words  # FALLBACK: return original list (safe!)


async def before_tool_callback(tool, args, tool_context: ToolContext):
    search_tools = ['search-papers-enhanced', 'web-search']
    logger.info(f"[before_tool_callback] Tool '{tool.name}' called with args: {args}")
    if tool.name not in search_tools:
        return

    words = args.get('words', [])
    page_size = args.get('page_size')
    if page_size is None:
        return
    else:
        page_size = max(MIN_page_size, int(page_size))
    args['page_size'] = int(page_size)
    if isinstance(words, str):
        words = [w.strip() for w in words.split()] if words.strip() else []
    elif not isinstance(words, list):
        logger.warning(f"'words' is unexpected type {type(words)}, fallback to []")
        words = []

    if not words:
        return

    if any(isinstance(w, str) and contains_chinese(w) for w in words):
        logger.info(f"[before_tool_callback] Detected Chinese words: {words}")
        try:
            translated_words = translate_word_list_to_english(words)
            if isinstance(translated_words, list):
                args['words'] = translated_words
                logger.info(f"[before_tool_callback] Updated args: {args}")
                return
        except Exception as e:
            logger.error(f"Unexpected error in translation flow: {e}")
        logger.info(f"[before_tool_callback] Translated words: {translated_words}")
    return


if __name__ == '__main__':
    # DEBUG
    chinese_words = ['含能材料DAP-4', 'DeePMD势函数', 'DPA预训练模型']
    translated_words = translate_word_list_to_english(chinese_words)
    logger.debug(f"[DEBUG] Translated words: {translated_words}")
