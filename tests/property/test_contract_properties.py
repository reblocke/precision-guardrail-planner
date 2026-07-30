from __future__ import annotations

import json
import math

from hypothesis import given
from hypothesis import strategies as st

from precision_guardrail import PlanningRequest, calculate_json


@given(
    current_se=st.floats(
        min_value=0.02,
        max_value=2.0,
        allow_nan=False,
        allow_infinity=False,
    ),
    true_effect=st.floats(
        min_value=0.02,
        max_value=3.0,
        allow_nan=False,
        allow_infinity=False,
    ),
    probability=st.floats(
        min_value=0.1,
        max_value=0.99,
        allow_nan=False,
        allow_infinity=False,
    ),
)
def test_feasible_response_is_strict_json_and_obeys_multiplier_identity(
    current_se: float,
    true_effect: float,
    probability: float,
) -> None:
    request = PlanningRequest(
        precision_mode="direct_se",
        effect_type="mean_difference",
        standard_error=current_se,
        ci_lower=None,
        ci_upper=None,
        null_value=0.0,
        target_true_effect=true_effect,
        alpha=0.05,
        selection_rule="two_sided_p_lt_alpha",
        claim_direction="positive",
        claim_threshold=None,
        minimum_selected_claim_probability=probability,
        maximum_type_s=None,
        maximum_type_m=None,
        sensitivity_enabled=False,
        sensitivity_min=None,
        sensitivity_max=None,
        sensitivity_points=19,
        sample_size_projection_enabled=False,
        current_effective_n=None,
    )
    payload = json.loads(calculate_json(json.dumps(request.__dict__)))
    joint = payload["joint_result"]

    if joint["feasible"]:
        required_se = joint["required_se_working"]
        multiplier = joint["required_information_multiplier"]
        assert math.isfinite(required_se)
        assert math.isfinite(multiplier)
        assert math.isclose(multiplier, (current_se / required_se) ** 2, rel_tol=1e-14)
    json.dumps(payload, allow_nan=False)
