from typing import List, Literal, Optional

from pydantic import BaseModel, create_model

from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum


def create_dynamic_plan_schema(available_tools: list):
    # 动态创建 PlanStepToolSchema
    DynamicPlanStepToolSchema = create_model(
        'DynamicPlanStepToolSchema',
        tool_name=(Optional[Literal[tuple(available_tools)]], None),
        description=(str, ...),
        status=(
            Literal[tuple(PlanStepStatusEnum.__members__.values())],
            PlanStepStatusEnum.PLAN.value,
        ),
        __base__=BaseModel,
    )

    # 动态创建 PlanStepSchema
    DynamicPlanStepSchema = create_model(
        'DynamicPlanStepSchema',
        tools=(List[DynamicPlanStepToolSchema], ...),
        relationship=(Literal['any', 'all'], ...),
        __base__=BaseModel,
    )

    # 动态创建 PlanSchema
    DynamicPlanSchema = create_model(
        'DynamicPlanSchema',
        steps=(List[DynamicPlanStepSchema], ...),
        __base__=BaseModel,
    )

    return DynamicPlanSchema
