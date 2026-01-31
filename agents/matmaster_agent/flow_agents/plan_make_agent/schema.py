from typing import List, Literal, Optional

from pydantic import BaseModel, create_model

from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum


def create_dynamic_multi_plans_schema(available_tools: list):
    # 动态创建 PlanStepSchema（可选目标级字段供 Step Executor 使用）
    DynamicPlanStepSchema = create_model(
        'DynamicPlanStepSchema',
        tool_name=(Optional[Literal[tuple(available_tools)]], None),
        step_description=(str, ...),
        feasibility=(str, ...),
        status=(
            Literal[tuple(PlanStepStatusEnum.__members__.values())],
            PlanStepStatusEnum.PLAN.value,
        ),
        expected_inputs=(Optional[List[str]], None),
        expected_outputs=(Optional[List[str]], None),
        success_criteria=(Optional[str], None),
        __base__=BaseModel,
    )

    # 动态创建 PlanSchema
    DynamicPlanSchema = create_model(
        'DynamicPlanSchema',
        plan_id=(str, ...),
        plan_description=(str, ...),
        steps=(List[DynamicPlanStepSchema], ...),
        __base__=BaseModel,
    )

    # 动态创建 MultiPlansSchema
    DynamicMultiPlansSchema = create_model(
        'DynamicMultiPlansSchema',
        intro=(str, ...),
        plans=(List[DynamicPlanSchema], ...),
        overall=(str, ...),
        __base__=BaseModel,
    )

    return DynamicMultiPlansSchema
