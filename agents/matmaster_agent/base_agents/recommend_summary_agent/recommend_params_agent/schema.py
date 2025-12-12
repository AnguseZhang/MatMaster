import logging
from typing import Any, Dict, List, Literal, Union

from google.genai import types
from pydantic import BaseModel, Field, create_model

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import PrefixFilter

GENAI_TYPE_TO_PYDANTIC_MAPPING = {
    types.Type.NUMBER: float,
    types.Type.STRING: str,
    types.Type.INTEGER: int,
    types.Type.BOOLEAN: bool,
}

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


def get_field_kwargs(field):
    # 添加字段描述（ 如果有 ）
    field_kwargs = {}
    for key in ['description', 'title', 'min_items', 'max_items']:
        if key in field:
            field_kwargs[key] = field[key]

    return field_kwargs


def get_field_type(field: Dict[str, Any]) -> Any:
    """递归获取字段类型，支持嵌套结构"""
    logger.info('field = {}'.format(field))
    if 'type' not in field:
        logger.warning(f'`{field}` dont have a type, default to object')

    field_type = field.get('type', types.Type.OBJECT)

    # 基本类型
    if field_type == types.Type.STRING:
        if field.get('enum'):
            return Literal[tuple(field['enum'])]
        else:
            return GENAI_TYPE_TO_PYDANTIC_MAPPING.get(field_type)

    elif field_type in GENAI_TYPE_TO_PYDANTIC_MAPPING:
        return GENAI_TYPE_TO_PYDANTIC_MAPPING.get(field_type)

    # 处理数组类型
    elif field_type == types.Type.ARRAY:
        if field.get('items'):
            item_type = get_field_type(field['items'])
            return List[item_type]
        else:
            logger.error(f'field = {field}')
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
            logger.error(f'field = {field}')
            raise NotImplementedError

    else:
        logger.error(f'field = {field}')
        raise NotImplementedError


def create_tool_args_schema(missing_tool_args, function_declaration):
    properties = function_declaration[0]['parameters']['properties']
    fields = {}

    for field_name in missing_tool_args:
        if field_name not in properties:
            logger.warning(f'{field_name} Not In Properties')
            continue
        field_schema = properties[field_name]
        field_type = get_field_type(field_schema)
        field_kwargs = get_field_kwargs(field_schema)

        fields[field_name] = (field_type, Field(..., **field_kwargs))

    DynamicToolArgsSchema = create_model(
        'DynamicToolArgsSchema',
        **fields,
        __base__=BaseModel,
    )
    logger.info(f'DynamicToolArgsSchema = {DynamicToolArgsSchema.model_json_schema()}')

    ToolSchema = create_model(
        'ToolSchema',
        tool_name=(str, Field(...)),
        tool_args=(DynamicToolArgsSchema, ...),
        missing_tool_args=(List[str], Field(default_factory=lambda: missing_tool_args)),
        __base__=BaseModel,
    )

    return DynamicToolArgsSchema, ToolSchema


if __name__ == '__main__':
    function_declaration = [
        {
            'parameters': {
                'properties': {
                    'stru_file': {'title': 'Stru File', 'type': 'STRING'},
                    'stru_type': {
                        'default': 'cif',
                        'enum': ['cif', 'poscar', 'abacus/stru'],
                        'title': 'Stru Type',
                        'type': 'STRING',
                    },
                    'lcao': {'default': True, 'title': 'Lcao', 'type': 'BOOLEAN'},
                    'nspin': {
                        'default': 1,
                        'enum': [1, 2],
                        'title': 'Nspin',
                        'type': 'INTEGER',
                    },
                    'dft_functional': {
                        'default': 'PBE',
                        'enum': [
                            'PBE',
                            'PBEsol',
                            'LDA',
                            'SCAN',
                            'HSE',
                            'PBE0',
                            'R2SCAN',
                        ],
                        'title': 'Dft Functional',
                        'type': 'STRING',
                    },
                    'dftu': {'default': False, 'title': 'Dftu', 'type': 'BOOLEAN'},
                    'dftu_param': {
                        'description': 'Definition of DFT+U params',
                        'properties': {
                            'element': {
                                'items': {'type': 'STRING'},
                                'title': 'Element',
                                'type': 'ARRAY',
                            },
                            'orbital': {
                                'items': {'enum': ['p', 'd', 'f'], 'type': 'STRING'},
                                'title': 'Orbital',
                                'type': 'ARRAY',
                            },
                            'U_value': {
                                'items': {'type': 'NUMBER'},
                                'title': 'U Value',
                                'type': 'ARRAY',
                            },
                        },
                        'required': ['element', 'orbital', 'U_value'],
                        'title': 'DFTUParam',
                        'type': 'OBJECT',
                    },
                    'init_mag': {
                        'description': 'Definition of initial magnetic params',
                        'properties': {
                            'element': {
                                'items': {'type': 'STRING'},
                                'title': 'Element',
                                'type': 'ARRAY',
                            },
                            'mag': {
                                'items': {'type': 'NUMBER'},
                                'title': 'Mag',
                                'type': 'ARRAY',
                            },
                        },
                        'required': ['element', 'mag'],
                        'title': 'InitMagParam',
                        'type': 'OBJECT',
                    },
                    'max_steps': {
                        'default': 100,
                        'title': 'Max Steps',
                        'type': 'INTEGER',
                    },
                    'relax': {'default': False, 'title': 'Relax', 'type': 'BOOLEAN'},
                    'relax_cell': {
                        'default': True,
                        'title': 'Relax Cell',
                        'type': 'BOOLEAN',
                    },
                    'relax_precision': {
                        'default': 'medium',
                        'enum': ['low', 'medium', 'high'],
                        'title': 'Relax Precision',
                        'type': 'STRING',
                    },
                    'relax_method': {
                        'default': 'cg',
                        'enum': ['cg', 'bfgs', 'bfgs_trad', 'cg_bfgs', 'sd', 'fire'],
                        'title': 'Relax Method',
                        'type': 'STRING',
                    },
                    'fixed_axes': {
                        'enum': [
                            'None',
                            'volume',
                            'shape',
                            'a',
                            'b',
                            'c',
                            'ab',
                            'ac',
                            'bc',
                        ],
                        'title': 'Fixed Axes',
                        'type': 'STRING',
                    },
                    'vacuum_direction': {
                        'default': 'z',
                        'enum': ['x', 'y', 'z'],
                        'title': 'Vacuum Direction',
                        'type': 'STRING',
                    },
                    'dipole_correction': {
                        'default': False,
                        'title': 'Dipole Correction',
                        'type': 'BOOLEAN',
                    },
                    'executor': {
                        'any_of': [
                            {'type': 'OBJECT'},
                            {'nullable': True, 'type': 'OBJECT'},
                        ],
                        'title': 'Executor',
                        'type': 'OBJECT',
                    },
                    'storage': {
                        'any_of': [
                            {'type': 'OBJECT'},
                            {'nullable': True, 'type': 'OBJECT'},
                        ],
                        'title': 'Storage',
                        'type': 'OBJECT',
                    },
                },
                'required': ['stru_file'],
                'title': 'abacus_cal_work_functionArguments',
                'type': 'OBJECT',
            }
        }
    ]

    missing_tool_args = ['fixed_axes']

    DynamicToolArgsSchema, ToolSchema = create_tool_args_schema(
        missing_tool_args, function_declaration
    )
    model_json_schema = DynamicToolArgsSchema.model_json_schema()
