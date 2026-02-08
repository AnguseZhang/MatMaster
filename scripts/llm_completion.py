import os
import time

from dotenv import find_dotenv, load_dotenv
from openai import AzureOpenAI, OpenAI

load_dotenv(find_dotenv())

USER_MESSAGE = 'hi'


def run_stream_stats(client, model, label, *, max_tokens=16384, temperature=None):
    """流式请求并统计 TTFT、总耗时、token 数。"""
    kwargs = {
        'messages': [{'role': 'user', 'content': USER_MESSAGE}],
        'max_completion_tokens': max_tokens,
        'model': model,
        'stream': True,
        'stream_options': {'include_usage': True},
    }
    if temperature is not None:
        kwargs['temperature'] = temperature

    t0 = time.perf_counter()
    ttft = None
    content_parts = []
    usage = None

    stream = client.chat.completions.create(**kwargs)

    for chunk in stream:
        if ttft is None and chunk.choices and chunk.choices[0].delta.content:
            ttft = time.perf_counter() - t0
        if chunk.choices and chunk.choices[0].delta.content:
            part = chunk.choices[0].delta.content
            content_parts.append(part)
            print(part, end='', flush=True)
        if getattr(chunk, 'usage', None) is not None:
            usage = chunk.usage

    elapsed = time.perf_counter() - t0
    print()
    print(f"\n[{label}]")
    print(
        f"  首 token 耗时 (TTFT): {ttft:.3f}s"
        if ttft is not None
        else '  首 token 耗时: N/A'
    )
    print(f"  总耗时: {elapsed:.3f}s")
    if usage and getattr(usage, 'total_tokens', None):
        total_tokens = usage.total_tokens
        if total_tokens > 0:
            print(
                f"  总 token 数: {total_tokens}, 约 {total_tokens / elapsed:.1f} tokens/s"
            )
    return ttft, elapsed, usage


# ---------- 1. Azure（.env：AZURE_API_KEY 等）----------
endpoint = os.environ.get('AZURE_API_BASE', 'https://physical4.openai.azure.com/')
api_key = os.environ.get('AZURE_API_KEY')
if not api_key:
    raise ValueError('请在 .env 中设置 AZURE_API_KEY')
deployment = os.environ.get('GPT_CHAT_MODEL', 'gpt-5-chat')
api_version = os.environ.get('AZURE_API_VERSION', '2025-01-01-preview')

client_azure = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=api_key,
)

print('=== Azure (GPT_CHAT_MODEL) ===')
run_stream_stats(client_azure, deployment, 'Azure', max_tokens=16384)

# ---------- 2. GPUGeek（OpenAI/Azure-GPT-5.1，.env：GPUGEEK_API_KEY）----------
gpugeek_key = os.environ.get('GPUGEEK_API_KEY')
gpugeek_base = os.environ.get('GPUGEEK_BASE_URL', 'https://api.gpugeek.com/v1')
gpugeek_model = os.environ.get('GPUGEEK_MODEL', 'OpenAI/Azure-GPT-5.1')

if gpugeek_key:
    client_gpugeek = OpenAI(api_key=gpugeek_key, base_url=gpugeek_base)
    print('\n=== GPUGeek (OpenAI/Azure-GPT-5.1) ===')
    run_stream_stats(
        client_gpugeek,
        gpugeek_model,
        'GPUGeek',
        max_tokens=2048,
        temperature=0.7,
    )
else:
    print('\n(跳过 GPUGeek：未设置 GPUGEEK_API_KEY)')
