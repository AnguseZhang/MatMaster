import asyncio
import base64
import json
import logging
import os
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def save_llm_request(llm_request, output_file):
    # 转换内容为字典并过滤掉null值
    contents_data = []
    for content in llm_request.contents:
        content_dict = content.model_dump()
        # 过滤掉parts中每个元素的null字段
        if "parts" in content_dict:
            filtered_parts = []
            for part in content_dict["parts"]:
                filtered_part = {k: v for k, v in part.items() if v is not None}
                filtered_parts.append(filtered_part)
            content_dict["parts"] = filtered_parts
        # 过滤掉顶层的null字段
        filtered_content = {k: v for k, v in content_dict.items() if v is not None}
        contents_data.append(filtered_content)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(contents_data, f, ensure_ascii=False, indent=2)


# OSS 上传功能
async def upload_base64_to_oss(data: str, oss_path: str) -> dict:
    """异步上传 base64 数据到 OSS"""
    return await asyncio.to_thread(_sync_upload_base64_to_oss, data, oss_path)


def _sync_upload_base64_to_oss(data: str, oss_path: str) -> dict:
    """同步上传 base64 数据到 OSS"""
    try:
        auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
        endpoint = os.environ["OSS_ENDPOINT"]
        bucket_name = os.environ["OSS_BUCKET_NAME"]
        bucket = oss2.Bucket(auth, endpoint, bucket_name)

        bucket.put_object(oss_path, base64.b64decode(data))
        return {
            "status": "success",
            "oss_path": f"https://{bucket_name}.oss-cn-zhangjiakou.aliyuncs.com/{oss_path}",
        }
    except Exception as e:
        logger.exception(
            f"[upload_base64_to_oss] OSS 上传失败: oss_path={oss_path} error={str(e)}"
        )
        return {"status": "failed", "reason": str(e)}