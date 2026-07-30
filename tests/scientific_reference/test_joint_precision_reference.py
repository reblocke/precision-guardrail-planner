from __future__ import annotations

import pytest
from wald_inference import design_metrics_for_true_effects

from precision_guardrail import PlanningRequest, calculate


def _response(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "precision_mode": "direct_se",
        "effect_type": "mean_difference",
        "standard_error": 0.75,
        "ci_lower": None,
        "ci_upper": None,
        "null_value": 0.0,
        "target_true_effect": 0.5,
        "alpha": 0.05,
        "selection_rule": "two_sided_p_lt_alpha",
        "claim_direction": "positive",
        "claim_threshold": None,
        "minimum_selected_claim_probability": 0.8,
        "maximum_type_s": 0.01,
        "maximum_type_m": 1.25,
        "sensitivity_enabled": False,
        "sensitivity_min": None,
        "sensitivity_max": None,
        "sensitivity_points": 19,
        "sample_size_projection_enabled": False,
        "current_effective_n": None,
    }
    payload.update(overrides)
    return calculate(PlanningRequest.from_mapping(payload)).to_payload()


def test_each_solved_row_hits_its_forward_core_metric() -> None:
    response = _response()

    for row in response["per_target_results"]:
        [metric] = design_metrics_for_true_effects(
            [response["target_effect"]["assumed_true_effect_working"]],
            null_working=response["target_effect"]["null_working"],
            se=row["required_se_working"],
            alpha=response["selection_rule"]["alpha"],
            selection_rule=response["selection_rule"]["key"],
            claim_direction=response["selection_rule"]["claim_direction"],
            threshold_working=response["selection_rule"]["claim_threshold_working"],
        )
        if row["target_key"] == "Power":
            assert metric.selected_claim_probability >= row["requested_value"]
        elif row["target_key"] == "Maximum Type S":
            assert metric.type_s is not None and metric.type_s <= row["requested_value"]
        else:
            assert metric.type_m is not None and metric.type_m <= row["requested_value"]


def test_joint_is_strictest_finite_target_and_width_identity() -> None:
    response = _response()
    rows = response["per_target_results"]
    joint = response["joint_result"]

    assert joint["required_se_working"] == min(row["required_se_working"] for row in rows)
    assert joint["required_information_multiplier"] == max(
        row["required_information_multiplier"] for row in rows
    )
    assert joint["approx_95_ci_width_working"] == pytest.approx(
        2.0 * 1.959963984540054 * joint["required_se_working"]
    )
    assert joint["required_information_multiplier"] == pytest.approx(
        (0.75 / joint["required_se_working"]) ** 2,
        rel=1e-15,
    )


def test_stricter_type_m_guardrail_requires_at_least_as_much_information() -> None:
    looser = _response(
        minimum_selected_claim_probability=None,
        maximum_type_s=None,
        maximum_type_m=1.5,
    )
    stricter = _response(
        minimum_selected_claim_probability=None,
        maximum_type_s=None,
        maximum_type_m=1.25,
    )

    assert (
        stricter["joint_result"]["required_information_multiplier"]
        > looser["joint_result"]["required_information_multiplier"]
    )
