from typing import List, Literal, Optional

from pydantic import BaseModel, create_model

from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum


def create_dynamic_multi_plans_schema(available_tools: list):
    # 动态创建 PlanStepSchema
    DynamicPlanStepSchema = create_model(
        'DynamicPlanStepSchema',
        tool_name=(Optional[Literal[tuple(available_tools)]], None),
        description=(str, ...),
        feasibility=(str, ...),
        status=(
            Literal[tuple(PlanStepStatusEnum.__members__.values())],
            PlanStepStatusEnum.PLAN.value,
        ),
        __base__=BaseModel,
    )

    # 动态创建 PlanSchema
    DynamicPlanSchema = create_model(
        'DynamicPlanSchema',
        plan_id=(str, ...),
        strategy=(str, ...),
        steps=(List[DynamicPlanStepSchema], ...),
        __base__=BaseModel,
    )

    # 动态创建 MultiPlansSchema
    DynamicMultiPlansSchema = create_model(
        'DynamicMultiPlansSchema',
        plans=(List[DynamicPlanSchema], ...),
        __base__=BaseModel,
    )

    return DynamicMultiPlansSchema
