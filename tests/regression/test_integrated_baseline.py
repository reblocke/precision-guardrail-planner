from __future__ import annotations

import json
from pathlib import Path

import pytest

from precision_guardrail import PlanningRequest, calculate

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "integrated_baseline"
    / "precision_b06_b07.json"
)


def _request(**overrides: object) -> PlanningRequest:
    payload: dict[str, object] = {
        "precision_mode": "direct_se",
        "effect_type": "mean_difference",
        "standard_error": 0.15816617164664273,
        "ci_lower": None,
        "ci_upper": None,
        "null_value": 0.0,
        "target_true_effect": 0.2,
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
    return PlanningRequest.from_mapping(payload)


def test_b06_core_owned_target_values_match_frozen_integrated_baseline() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    response = calculate(_request()).to_payload()

    assert (
        response["current_precision"]["current_se_working"] == fixture["b06"]["current_se_working"]
    )
    for actual, expected in zip(
        response["per_target_results"],
        fixture["b06"]["targets"],
        strict=True,
    ):
        assert actual["target_key"] == expected["target"]
        assert actual["requested_value"] == expected["requested_value"]
        assert actual["required_se_working"] == pytest.approx(
            expected["required_se"],
            rel=1e-12,
            abs=1e-14,
        )
        assert actual["required_information_multiplier"] == pytest.approx(
            expected["required_information_multiplier"],
            rel=1e-12,
            abs=1e-14,
        )
        assert actual["approx_95_ci_width_working"] == pytest.approx(
            expected["approx_95_ci_width_working"],
            rel=1e-12,
            abs=1e-14,
        )
        for actual_key, expected_key in [
            ("achieved_selected_claim_probability", "achieved_power"),
            ("achieved_type_s", "achieved_type_s"),
            ("achieved_type_m", "achieved_type_m"),
        ]:
            assert actual[actual_key] == pytest.approx(
                expected[expected_key],
                rel=1e-12,
                abs=1e-14,
            )


def test_b07_null_and_threshold_infeasibility_notes_are_preserved() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    null = calculate(_request(target_true_effect=0.0)).to_payload()
    threshold = calculate(
        _request(
            target_true_effect=0.1,
            selection_rule="ci_excludes_mcid",
            claim_threshold=0.2,
            maximum_type_s=None,
            maximum_type_m=None,
        )
    ).to_payload()

    assert null["per_target_results"][0]["solver_note"] == fixture["b07"]["null_target_note"]
    assert (
        threshold["per_target_results"][0]["solver_note"]
        == fixture["b07"]["threshold_infeasible_note"]
    )
