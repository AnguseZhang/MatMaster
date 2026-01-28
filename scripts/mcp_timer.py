import asyncio
import os
import time
import traceback
from typing import Any, Dict, List

from dotenv import load_dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    SseServerParams,
    StreamableHTTPServerParams,
)


class Timer:
    """Timer class for measuring tool execution time."""

    def __init__(self, name: str = 'Timer'):
        """
        Initialize the timer.

        Args:
            name: Name of the timer for identification
        """
        self.name = name
        self.start_time = None
        self.end_time = None

    def start(self):
        """Start the timer."""
        self.start_time = time.time()
        print(
            f"{self.name} started at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))}"
        )

    def stop(self):
        """Stop the timer."""
        self.end_time = time.time()
        print(
            f"{self.name} stopped at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.end_time))}"
        )

    def elapsed_time(self) -> float:
        """
        Get the elapsed time in seconds.

        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None:
            raise ValueError("Timer hasn't been started yet")

        if self.end_time is None:
            # Return time since start if timer is still running
            return time.time() - self.start_time
        else:
            return self.end_time - self.start_time

    def elapsed_time_str(self) -> str:
        """
        Get the elapsed time as a formatted string.

        Returns:
            Formatted elapsed time string
        """
        elapsed = self.elapsed_time()
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = elapsed % 60

        parts = []
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        parts.append(f"{seconds:.2f} second{'s' if seconds != 1 else ''}")

        return ', '.join(parts)


class MCPTimer:
    """Class to test MCP tools with timing capabilities."""

    def __init__(self, url: str, storage_type: str = 'https'):
        """
        Initialize MCP Timer.

        Args:
            url: URL for the MCP connection
            storage_type: Type of storage to use ("https", "local", "bohrium")
        """
        # Modify load_dotenv() to explicit override mode
        load_dotenv(override=True)

        self.LOCAL_EXECUTOR = {'type': 'local'}
        self.BOHRIUM_STORAGE = {
            'type': 'bohrium',
            'username': os.getenv('BOHRIUM_EMAIL'),
            'password': os.getenv('BOHRIUM_PASSWORD'),
            'project_id': int(os.getenv('BOHRIUM_PROJECT_ID')),
        }
        self.HTTPS_STORAGE = {
            'type': 'https',
            'plugin': {
                'type': 'bohrium',
                'access_key': os.getenv('BOHRIUM_ACCESS_KEY'),
                'project_id': int(os.getenv('BOHRIUM_PROJECT_ID')),
            },
        }

        # Select storage based on type
        if storage_type == 'https':
            storage = self.HTTPS_STORAGE
        elif storage_type == 'bohrium':
            storage = self.BOHRIUM_STORAGE
        else:
            storage = self.LOCAL_EXECUTOR

        print(f'Using storage configuration: {storage}')

        if 'sse' in url.lower():
            connection_params = SseServerParams(url=url)
        else:
            connection_params = StreamableHTTPServerParams(url=url)

        self.mcp_toolset = CalculationMCPToolset(
            connection_params=connection_params,
            storage=storage,
            executor=None,
        )

    async def cleanup(self):
        """Clean up MCP resources."""
        print('Cleaning up MCP resources...')
        if hasattr(self.mcp_toolset, 'close'):
            # If toolset has a close method (might be async)
            if asyncio.iscoroutinefunction(self.mcp_toolset.close):
                await self.mcp_toolset.close()
            else:
                self.mcp_toolset.close()
        elif hasattr(self.mcp_toolset, 'client'):
            # If toolset wraps a client, try closing the client
            client = self.mcp_toolset.client
            if hasattr(client, 'close'):
                if asyncio.iscoroutinefunction(client.close):
                    await client.close()
                else:
                    client.close()
            # For mcp-python-sdk, sometimes need to close session
            if hasattr(client, 'session') and hasattr(client.session, 'close'):
                if asyncio.iscoroutinefunction(client.session.close):
                    await client.session.close()
                else:
                    client.session.close()

        print('Cleanup completed.')

    async def test_single_tool(
        self, tool_name: str, args: Dict[str, Any], timeout_seconds: int = 3600
    ) -> Dict[str, Any]:
        """
        Test a single tool and measure its execution time.

        Args:
            tool_name: Name of the tool to test
            args: Arguments to pass to the tool
            timeout_seconds: Timeout in seconds for the tool execution

        Returns:
            Dictionary containing result and timing information
        """
        timer = Timer(f"Tool '{tool_name}' execution")

        try:
            tools = await self.mcp_toolset.get_tools()
            target_tool = next((t for t in tools if t.name == tool_name), None)

            if target_tool is None:
                return {
                    'error': f"Tool {tool_name} not found",
                    'elapsed_time': timer.elapsed_time(),
                    'elapsed_time_str': timer.elapsed_time_str(),
                }

            print(f"Testing tool: {tool_name}")
            timer.start()
            result = await asyncio.wait_for(
                target_tool.run_async(args=args, tool_context=None),
                timeout=timeout_seconds,
            )

            timer.stop()
            return {
                'result': result,
                'elapsed_time': timer.elapsed_time(),
                'elapsed_time_str': timer.elapsed_time_str(),
                'success': True,
            }

        except asyncio.TimeoutError:
            timer.stop()
            return {
                'error': f"Tool {tool_name} timed out after {timeout_seconds} seconds",
                'elapsed_time': timer.elapsed_time(),
                'elapsed_time_str': timer.elapsed_time_str(),
                'success': False,
            }

        except Exception as e:
            timer.stop()
            return {
                'error': f"Error testing {tool_name}: {str(e)}\n{traceback.format_exc()}",
                'elapsed_time': timer.elapsed_time(),
                'elapsed_time_str': timer.elapsed_time_str(),
                'success': False,
            }

    async def test_multiple_tools(
        self, tool_calls: List[Dict[str, Any]], timeout_seconds: int = 3600
    ) -> List[Dict[str, Any]]:
        """
        Test multiple tools sequentially and measure their execution times.

        Args:
            tool_calls: List of tool calls in the format {"functionCall": {"name": "...", "args": {...}}}
            timeout_seconds: Timeout in seconds for each tool execution

        Returns:
            List of results with timing information for each tool
        """
        total_timer = Timer('Total execution')
        total_timer.start()

        results = []

        for i, tool_call in enumerate(tool_calls):
            function_call = tool_call.get('functionCall', {})
            tool_name = function_call.get('name')
            args = function_call.get('args', {})

            if not tool_name:
                print(f"Skipping tool call {i+1} - no name specified")
                continue

            print(f"\n--- Testing tool {i+1}/{len(tool_calls)}: {tool_name} ---")

            result = await self.test_single_tool(tool_name, args, timeout_seconds)
            result['tool_name'] = tool_name
            result['args'] = args
            results.append(result)

            print(
                f"Completed tool {tool_name}. Result: {'Success' if result.get('success', False) else 'Failed'}"
            )
            print(f"Elapsed time: {result['elapsed_time_str']}")

        total_timer.stop()
        print(f"\nTotal execution time: {total_timer.elapsed_time_str()}")

        return results


if __name__ == '__main__':
    url = 'http://pfmx1355864.bohrium.tech:50005/mcp'

    tool_calls = [
        {
            'functionCall': {
                'name': 'extract_info_from_webpage',
                'args': {
                    'url': [
                        'https://docs.lammps.org/fix_msst.html',
                    ],
                    'additional_prompt': 'Retry extracting detailed explanations and insights about ferrotoroidicity phase transitions, including their definition, microscopic origin, symmetry properties, and role in multiferroic materials from the specified documents.',
                },
            }
        }
    ]

    # Add better error handling for the entire execution
    async def safe_main():
        mcp_timer = None  # Initialize to None to prevent errors if creation fails
        try:
            timer = Timer('Main execution')
            timer.start()

            mcp_timer = MCPTimer(url, 'https')

            # Test multiple tools
            results = await mcp_timer.test_multiple_tools(tool_calls)

            # Print summary
            print('\n=== EXECUTION SUMMARY ===')
            successful = sum(1 for r in results if r.get('success', False))
            failed = len(results) - successful
            print(f"Total tools tested: {len(results)}")
            print(f"Successful: {successful}")
            print(f"Failed: {failed}")

            for result in results:
                status = '✓ Success' if result.get('success', False) else '✗ Failed'
                print(
                    f"- {status}: {result['tool_name']} ({result['elapsed_time_str']})"
                )

            timer.stop()
            print(f"Overall execution time: {timer.elapsed_time_str()}")

        except Exception as e:
            print(f"Error in main execution: {e}")
            print(traceback.format_exc())
        finally:
            # Explicitly close connections
            if mcp_timer:
                await mcp_timer.cleanup()

            # Allow time for cleanup
            await asyncio.sleep(0.2)

    # Run the main function with better error handling
    try:
        asyncio.run(safe_main())
    except KeyboardInterrupt:
        print('Execution interrupted by user')
    except Exception as e:
        print(f"Unhandled error: {e}")
        print(traceback.format_exc())
