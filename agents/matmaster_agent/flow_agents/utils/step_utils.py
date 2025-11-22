from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum


def get_step_status(step):
    step_relationship = step['relationship']
    if step_relationship == 'any':
        if all(tool['status'] == PlanStepStatusEnum.PLAN for tool in step['tools']):
            return PlanStepStatusEnum.PLAN
        elif any(
            tool['status'] in [PlanStepStatusEnum.PROCESS, PlanStepStatusEnum.SUBMITTED]
            for tool in step['tools']
        ):
            return PlanStepStatusEnum.PROCESS
        elif all(tool['status'] == PlanStepStatusEnum.FAILED for tool in step['tools']):
            return PlanStepStatusEnum.FAILED
        elif any(
            tool['status'] == PlanStepStatusEnum.SUCCESS for tool in step['tools']
        ):
            return PlanStepStatusEnum.SUCCESS
    elif step_relationship == 'all':
        if any(tool['status'] == PlanStepStatusEnum.PLAN for tool in step['tools']):
            return PlanStepStatusEnum.PLAN
        elif any(
            tool['status'] in [PlanStepStatusEnum.PROCESS, PlanStepStatusEnum.SUBMITTED]
            for tool in step['tools']
        ):
            return PlanStepStatusEnum.PROCESS
        elif any(tool['status'] == PlanStepStatusEnum.FAILED for tool in step['tools']):
            return PlanStepStatusEnum.FAILED
    else:
        raise TypeError(f'step_relationship = {step_relationship}')
