from typing import Optional, Any

from dotenv import load_dotenv
from opik.evaluation.metrics import base_metric, score_result

from agents.matmaster_agent.utils.helper_func import is_same_function_call
from evaluate.constant import TRANSFER_TO_AGENT_QUALITY

load_dotenv()


class TransferToAgentQuality(base_metric.BaseMetric):
    def __init__(
            self,
            name: str = TRANSFER_TO_AGENT_QUALITY,
            model: Optional[str] = "azure/gpt-4o",
            ignore_whitespace: bool = True,
            track: bool = True,
            project_name: Optional[str] = None,
    ):
        self.model = model
        self.ignore_whitespace = ignore_whitespace
        super().__init__(name=name, track=track, project_name=project_name)

    def score(
            self,
            output: str,
            function_call: dict,
            expected_function_call: dict,
            **kwargs: Any,
    ) -> score_result.ScoreResult:
        try:

            if is_same_function_call(function_call, expected_function_call):
                return score_result.ScoreResult(
                    name=self.name,
                    value=1
                )
            else:
                return score_result.ScoreResult(
                    name=self.name,
                    value=0,
                    reason=f"current_function_call: {function_call},"
                           f"expected_function_call: {expected_function_call}"
                )
        except Exception as e:
            print(e)
            return score_result.ScoreResult(
                name=self.name,
                value=0,
                reason=f"Scoring error: {str(e)}"
            )
