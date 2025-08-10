import json


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