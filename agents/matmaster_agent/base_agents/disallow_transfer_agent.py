from typing import Any

from pydantic import model_validator

from agents.matmaster_agent.base_agents.abc_agent import BaseMixin
from agents.matmaster_agent.base_agents.error_agent import ErrorHandleLlmAgent


class DisallowTransferMixin(BaseMixin):
    @model_validator(mode='before')
    @classmethod
    def decorate_callbacks(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        data['disallow_transfer_to_parent'] = True
        data['disallow_transfer_to_peers'] = True

        return data


class DisallowTransferLlmAgent(DisallowTransferMixin, ErrorHandleLlmAgent):
    pass
