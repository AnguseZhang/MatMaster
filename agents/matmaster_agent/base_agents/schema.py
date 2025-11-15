from typing import Any, Dict, List, Union

from google.genai import types
from pydantic import BaseModel, Field, create_model

GENAI_TYPE_TO_PYDANTIC_MAPPING = {
    types.Type.NUMBER: float,
    types.Type.STRING: str,
    types.Type.INTEGER: int,
}


def get_field_kwargs(field):
    # 添加字段描述（如果有）
    field_kwargs = {}
    for key in ['description', 'title', 'min_items', 'max_items']:
        if key in field:
            field_kwargs[key] = field[key]

    return field_kwargs


def get_field_type(field: Dict[str, Any]) -> Any:
    """递归获取字段类型，支持嵌套结构"""
    field_type = field['type']

    # 基本类型
    if field_type in [types.Type.NUMBER, types.Type.STRING, types.Type.INTEGER]:
        return GENAI_TYPE_TO_PYDANTIC_MAPPING.get(field_type)

    # 处理数组类型
    elif field_type == types.Type.ARRAY:
        if field.get('items'):
            item_type = get_field_type(field['items'])
            return List[item_type]
        else:
            raise NotImplementedError

    # 处理对象类型
    elif field_type == types.Type.OBJECT:
        if field.get('properties'):
            # 递归创建嵌套的Pydantic模型
            nested_fields = {}
            for prop_name, prop_schema in field['properties'].items():
                prop_type = get_field_type(prop_schema)
                prop_kwargs = get_field_kwargs(prop_schema)
                nested_fields[prop_name] = (prop_type, Field(..., **prop_kwargs))

            # 创建嵌套模型
            nested_model_name = field.get('title', 'NestedModel')
            NestedModel = create_model(
                nested_model_name, **nested_fields, __base__=BaseModel
            )
            return NestedModel
        # 处理 any_of 类型（联合类型）
        elif field.get('any_of'):
            any_of_types = []
            for any_of_type in field['any_of']:
                if any_of_type.get('nullable'):
                    # 处理可空类型
                    if any_of_type['type'] == types.Type.OBJECT:
                        any_of_types.append(type(None))
                    else:
                        raise NotImplementedError
                else:
                    any_of_types.append(get_field_type(any_of_type))
            return Union[tuple(any_of_types)]
        else:
            raise NotImplementedError

    else:
        raise NotImplementedError


def create_tool_args_schema(missing_tool_args, function_declaration):
    properties = function_declaration[0]['parameters']['properties']
    fields = {}

    for field_name in missing_tool_args:
        field_schema = properties[field_name]
        field_type = get_field_type(field_schema)
        field_kwargs = get_field_kwargs(field_schema)

        fields[field_name] = (field_type, Field(..., **field_kwargs))

    DynamicToolArgsSchema = create_model(
        'DynamicToolArgsSchema',
        **fields,
        __base__=BaseModel,
    )

    return DynamicToolArgsSchema


if __name__ == '__main__':
    import pickle

    missing_tool_args = [
        'a',
        'b',
        'c',
        'alpha',
        'beta',
        'gamma',
        'spacegroup',
        'wyckoff_positions',
    ]
    with open(
        '/Users/hui_zhou/Project/AtomSmith/MatMaster/agents/matmaster_agent/function_declaration',
        'rb',
    ) as f:
        function_declaration = pickle.load(f)

    DynamicToolArgsSchema = create_tool_args_schema(
        missing_tool_args, function_declaration
    )
    model_json_schema = DynamicToolArgsSchema.model_json_schema()
