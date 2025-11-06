import json
from typing import Union

from google.adk.tools import BaseTool

from agents.matmaster_agent.sub_agents.chembrain_agent.retrosyn_agent.constant import (
    GeneratedImagesKey,
    PlanVisualizeReactionTool,
)
from agents.matmaster_agent.sub_agents.chembrain_agent.retrosyn_agent.utils import (
    extract_convert_and_upload,
)
from agents.matmaster_agent.sub_agents.chembrain_agent.utils import is_json


# after_tool_callback
async def retrosyn_after_tool_transform_tgz(
    tool: BaseTool, args, tool_context, tool_response
) -> Union[dict, None]:
    if tool.name != PlanVisualizeReactionTool:
        return None
    else:
        if not (
            tool_response
            and tool_response.content
            and tool_response.content[0].text
            and is_json(tool_response.content[0].text)
            and json.loads(tool_response.content[0].text).get(GeneratedImagesKey, None)
            is not None
        ):
            return None

        try:
            tgz_url = json.loads(tool_response.content[0].text)[GeneratedImagesKey]
            results = await extract_convert_and_upload(tgz_url)
            for filename, result in results.items():
                if result['status'] == 'success':
                    results[filename][
                        'markdown_image'
                    ] = f"![{filename}]({result['oss_path']})"
            results['origin_tool_response'] = tgz_url
            return results
        except Exception as e:
            return {'error_msg': str(e)}
