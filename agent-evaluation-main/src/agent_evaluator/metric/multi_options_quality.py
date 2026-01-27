from typing import Any, List, Optional, Union

from dotenv import load_dotenv
from opik.evaluation.metrics import base_metric, score_result
from opik.evaluation.metrics.llm_judges.parsing_helpers import (
    extract_json_content_or_raise,
)
from opik.evaluation.models import base_model, models_factory
from pydantic import BaseModel

from ..constant import MULTI_OPTION_QUALITY

load_dotenv(override=True)


class MultiOptionResponseFormat(BaseModel):
    score: float
    reason: List[str]


class MultiOptionQuality(base_metric.BaseMetric):
    def __init__(
        self,
        name: str = MULTI_OPTION_QUALITY,
        model: Optional[str] = 'azure/gpt-4o',
        ignore_whitespace: bool = True,
        track: bool = True,
        project_name: Optional[str] = None,
    ):
        self.model = model
        self.ignore_whitespace = ignore_whitespace
        super().__init__(name=name, track=track, project_name=project_name)
        self._init_model(model)

    def _init_model(
        self, model: Optional[Union[str, base_model.OpikBaseModel]]
    ) -> None:
        if isinstance(model, base_model.OpikBaseModel):
            self._model = model
        else:
            self._model = models_factory.get(model_name=model)

    def generate_query(self, input: str, output: str) -> str:
        output_template = """
        You are an expert judge tasked with evaluating whether an AI-generated response provides clear and relevant options to the user. Analyze the provided INPUT and OUTPUT to determine if the OUTPUT contains multiple actionable choices for the user.

        Guidelines:
        1. **Option Presence**: The OUTPUT must explicitly offer at least two distinct options (e.g., "生成结构" vs. "数据库检索").
        2. **Option Clarity**: Each option should be unambiguous and phrased in a way that users can easily understand (e.g., avoid vague terms like "maybe try X").
        3. **Option Relevance**: The options must directly address the user's INPUT (e.g., if the user asks about "table structure," options should relate to data generation/retrieval, not unrelated actions).
        4. **Actionability**: Options should be executable by the user (e.g., buttons, commands, or clear instructions).

        Scoring Criteria:
        - **1.0 (Fully Compliant)**: OUTPUT meets all guidelines (multiple, clear, relevant, actionable options).
        - **0.5 (Partially Compliant)**: OUTPUT partially meets guidelines (e.g., only one option, or options are unclear).
        - **0.0 (Non-Compliant)**: OUTPUT fails to provide any valid options.

        INPUT (user query for context):
        {input}

        OUTPUT (AI-generated response to evaluate):
        {output}

        Provide your evaluation in the following JSON format:
        {{
            "score": <0.0, 0.5, or 1.0>,
            "reason": ["specific reason 1", "specific reason 2"],
        }}
        """

        return output_template.format(input=input, output=output)

    def score(
        self,
        input: str,
        output: str,
        function_call: dict,
        expected_function_call: dict,
        **kwargs: Any,
    ) -> score_result.ScoreResult:
        try:
            llm_query = self.generate_query(input=input, output=output)
            model_output = self._model.generate_string(
                input=llm_query, response_format=MultiOptionResponseFormat
            )

            dict_content = extract_json_content_or_raise(model_output)
            score = float(dict_content['score'])

            if not (0.0 <= score <= 1.0):
                raise ValueError(f"Score must be between 0.0 and 1.0, got {score}")
            return score_result.ScoreResult(
                name=self.name,
                value=score,
                reason=str(dict_content['reason']),
            )
        except Exception as e:
            print(e)
            return score_result.ScoreResult(
                name=self.name, value=0, reason=f"Scoring error: {str(e)}"
            )
