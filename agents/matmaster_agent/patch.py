import asyncio
import json
import logging
from contextlib import contextmanager
from copy import deepcopy

import jsonpickle
from dp.agent.adapter.adk import CalculationMCPTool
from google.adk.tools import ToolContext

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import PrefixFilter

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


@contextmanager
def patch_CalculationMCPTool_run_async():
    original_CalculationMCPTool_run_async = CalculationMCPTool.run_async

    async def patched_run_async(self, args, tool_context: ToolContext, **kwargs):
        # TODO: add progress callback when run_async
        args = deepcopy(args)
        if self.override or 'executor' not in args:
            args['executor'] = self.executor
        if self.override or 'storage' not in args:
            args['storage'] = self.storage
        if not self.async_mode and self.wait:
            return await super(CalculationMCPTool, self).run_async(
                args=args, tool_context=tool_context, **kwargs
            )

        executor = args['executor']
        storage = args['storage']
        res = await self.submit_tool.run_async(
            args=args, tool_context=tool_context, **kwargs
        )
        logger.info(f'res = {res}')
        if res.isError:
            logger.error(res.content[0].text)
            return res
        job_id = json.loads(res.content[0].text)['job_id']
        job_info = res.content[0].job_info
        await self.log('info', 'Job submitted (ID: %s)' % job_id, tool_context)
        if job_info.get('extra_info'):
            await self.log('info', job_info['extra_info'], tool_context)
        if not self.wait:
            res.content[0].text = json.dumps(
                {
                    'job_id': job_id,
                    'status': 'Running',
                    'extra_info': job_info.get('extra_info'),
                }
            )
            return res

        while True:
            res = await self.query_tool.run_async(
                args={'job_id': job_id, 'executor': executor},
                tool_context=tool_context,
                **kwargs,
            )
            if res.isError:
                logger.error(res.content[0].text)
            else:
                status = res.content[0].text
                await self.log(
                    'info', 'Job {} status is {}'.format(job_id, status), tool_context
                )
                if status != 'Running':
                    break
            await asyncio.sleep(self.query_interval)

        res = await self.results_tool.run_async(
            args={'job_id': job_id, 'executor': executor, 'storage': storage},
            tool_context=tool_context,
            **kwargs,
        )
        if res.isError:
            await self.log(
                'error',
                'Job {} failed: {}'.format(job_id, res.content[0].text),
                tool_context,
            )
        else:
            await self.log(
                'info',
                'Job {} result is {}'.format(
                    job_id, jsonpickle.loads(res.content[0].text)
                ),
                tool_context,
            )
        res.content[0].job_info = {
            **job_info,
            **getattr(res.content[0], 'job_info', {}),
        }
        return res

    CalculationMCPTool.run_async = patched_run_async

    try:
        yield
    finally:
        CalculationMCPTool.run_async = original_CalculationMCPTool_run_async
