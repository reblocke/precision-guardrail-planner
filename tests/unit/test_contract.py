from __future__ import annotations

import json
import math
from collections.abc import Callable

import pytest

from precision_guardrail import (
    PlanningRequest,
    ValidationError,
    calculate,
    calculate_json,
)


def _calculate(payload: dict[str, object]):
    return calculate(PlanningRequest.from_mapping(payload)).to_payload()


def test_focused_contract_has_exact_sections_and_b06_values(
    planning_payload: Callable[..., dict[str, object]],
) -> None:
    response = _calculate(planning_payload())

    assert list(response) == [
        "meta",
        "current_precision",
        "assumptions",
        "selection_rule",
        "target_effect",
        "per_target_results",
        "joint_result",
        "sensitivity_optional",
        "sample_size_projection_optional",
        "warnings",
    ]
    assert response["meta"]["core_version"] == "0.4.2"
    assert [row["target_key"] for row in response["per_target_results"]] == [
        "Power",
        "Maximum Type S",
        "Maximum Type M",
    ]
    assert response["joint_result"]["required_se_working"] == pytest.approx(0.07138824202335431)
    assert response["joint_result"]["required_information_multiplier"] == pytest.approx(
        4.908782966731538
    )
    assert response["joint_result"]["binding_targets"] == ["Minimum selected-claim probability"]


def test_current_precision_sufficient_is_exactly_one_and_reports_ties(
    planning_payload: Callable[..., dict[str, object]],
) -> None:
    response = _calculate(
        planning_payload(
            standard_error=0.1,
            target_true_effect=1.0,
        )
    )
    joint = response["joint_result"]

    assert joint["feasible"]
    assert joint["current_precision_sufficient"]
    assert joint["required_information_multiplier"] == 1.0
    assert joint["required_information_multiplier"].hex() == "0x1.0000000000000p+0"
    assert joint["binding_targets"] == [
        "Minimum selected-claim probability",
        "Maximum Type S",
        "Maximum Type M",
    ]


def test_threshold_infeasibility_propagates_but_preserves_rows(
    planning_payload: Callable[..., dict[str, object]],
) -> None:
    response = _calculate(
        planning_payload(
            standard_error=1.0,
            target_true_effect=0.5,
            selection_rule="ci_excludes_mcid",
            claim_threshold=1.0,
            maximum_type_s=0.5,
            maximum_type_m=None,
        )
    )

    assert response["joint_result"]["status"] == "no_finite_joint_solution"
    assert [row["feasible"] for row in response["per_target_results"]] == [False, True]
    assert "not beyond the claim threshold" in response["joint_result"]["note"]
    assert response["per_target_results"][0]["required_information_multiplier"] is None
    assert "claim threshold of 1" in response["joint_result"]["reviewer_text"]


def test_near_null_type_s_and_type_m_remain_explicitly_infeasible(
    planning_payload: Callable[..., dict[str, object]],
) -> None:
    response = _calculate(planning_payload(target_true_effect=0.0))

    assert not response["joint_result"]["feasible"]
    assert all(not row["feasible"] for row in response["per_target_results"])
    assert all(
        row["achieved_type_s"] is None and row["achieved_type_m"] is None
        for row in response["per_target_results"]
    )
    assert "near the null" in response["joint_result"]["note"]


@pytest.mark.parametrize(
    ("selection_rule", "direction", "truth", "threshold"),
    [
        ("two_sided_p_lt_alpha", "positive", 0.5, None),
        ("one_sided_positive_p_lt_alpha", "positive", 0.5, None),
        ("one_sided_negative_p_lt_alpha", "negative", -0.5, None),
        ("ci_excludes_null_in_beneficial_direction", "positive", 0.5, None),
        ("estimate_exceeds_mcid_and_p_lt_alpha", "positive", 0.5, 0.2),
        ("ci_excludes_mcid", "positive", 0.5, 0.2),
    ],
)
def test_all_six_selected_claim_rules_produce_finite_solutions(
    planning_payload: Callable[..., dict[str, object]],
    selection_rule: str,
    direction: str,
    truth: float,
    threshold: float | None,
) -> None:
    response = _calculate(
        planning_payload(
            standard_error=0.75,
            target_true_effect=truth,
            selection_rule=selection_rule,
            claim_direction=direction,
            claim_threshold=threshold,
            maximum_type_s=None,
            maximum_type_m=None,
        )
    )

    assert response["joint_result"]["feasible"]
    assert (
        response["joint_result"]["achieved_selected_claim_probability"]
        >= response["per_target_results"][0]["requested_value"]
    )


def test_direct_se_and_ci_reconstruction_are_numerically_equivalent(
    planning_payload: Callable[..., dict[str, object]],
) -> None:
    direct = _calculate(planning_payload())
    reconstructed = _calculate(
        planning_payload(
            precision_mode="ci_95",
            standard_error=None,
            ci_lower=0.11,
            ci_upper=0.73,
        )
    )

    assert reconstructed["current_precision"]["current_se_working"] == pytest.approx(
        direct["current_precision"]["current_se_working"],
        rel=1e-15,
    )
    assert reconstructed["joint_result"]["required_se_working"] == pytest.approx(
        direct["joint_result"]["required_se_working"],
        rel=1e-15,
    )
    assert reconstructed["joint_result"]["required_information_multiplier"] == pytest.approx(
        direct["joint_result"]["required_information_multiplier"],
        rel=2e-15,
    )
    assert "not treated as the assumed truth" in reconstructed["current_precision"]["source_note"]


def test_ratio_inputs_use_log_working_scale(
    planning_payload: Callable[..., dict[str, object]],
) -> None:
    response = _calculate(
        planning_payload(
            effect_type="odds_ratio",
            standard_error=0.2,
            null_value=1.0,
            target_true_effect=1.5,
            maximum_type_s=None,
        )
    )

    assert response["target_effect"]["assumed_true_effect_working"] == pytest.approx(math.log(1.5))
    assert response["meta"]["working_scale"] == "log"
    assert any("log working scale" in warning for warning in response["warnings"])


def test_sensitivity_preserves_feasibility_gaps_and_monotonic_envelope(
    planning_payload: Callable[..., dict[str, object]],
) -> None:
    response = _calculate(
        planning_payload(
            maximum_type_s=None,
            sensitivity_enabled=True,
            sensitivity_min=0.0,
            sensitivity_max=0.8,
            sensitivity_points=5,
        )
    )
    rows = response["sensitivity_optional"]["rows"]
    finite = [
        row["joint_required_information_multiplier"]
        for row in rows
        if row["joint_required_information_multiplier"] is not None
    ]

    assert rows[0]["joint_feasible"] is False
    assert [row["true_effect_display"] for row in rows] == pytest.approx([0.0, 0.2, 0.4, 0.6, 0.8])
    assert finite == sorted(finite, reverse=True)
    assert response["sensitivity_optional"]["range_is_distribution"] is False


def test_sample_size_projection_is_opt_in_and_rounded_up(
    planning_payload: Callable[..., dict[str, object]],
) -> None:
    without_projection = _calculate(planning_payload())
    with_projection = _calculate(
        planning_payload(
            sample_size_projection_enabled=True,
            current_effective_n=100.0,
        )
    )

    assert without_projection["sample_size_projection_optional"] is None
    projection = with_projection["sample_size_projection_optional"]
    assert projection["approx_required_n"] == 491
    assert projection["assumption_active"] is True
    assert "not a design-specific" in projection["note"]


def test_extreme_requirement_is_infeasible_at_core_information_cap(
    planning_payload: Callable[..., dict[str, object]],
) -> None:
    response = _calculate(
        planning_payload(
            standard_error=1.0,
            target_true_effect=1e-6,
            minimum_selected_claim_probability=0.999999,
            maximum_type_s=None,
            maximum_type_m=None,
        )
    )

    assert not response["joint_result"]["feasible"]
    assert "supported maximum relative information multiplier" in response["joint_result"]["note"]


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_contract_rejects_nonstandard_json_numbers(
    planning_payload: Callable[..., dict[str, object]],
    constant: str,
) -> None:
    encoded = json.dumps(planning_payload())
    encoded = encoded.replace('"alpha": 0.05', f'"alpha": {constant}')

    with pytest.raises(ValidationError, match="Non-finite JSON constant"):
        calculate_json(encoded)


def test_contract_returns_strict_json_without_prohibited_output_families(
    planning_payload: Callable[..., dict[str, object]],
) -> None:
    response_json = calculate_json(json.dumps(planning_payload()))
    lowered = response_json.lower()

    assert "nan" not in lowered
    assert "infinity" not in lowered
    assert "relative_likelihood" not in lowered
    assert "compatibility" not in lowered
    assert "s_minus_2" not in lowered
    assert '"grid"' not in lowered
    assert json.loads(response_json)["meta"]["scope"] == "inverse_precision_guardrails_only"


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"alpha": 0.0}, "Alpha must be between"),
        ({"alpha": 1.0}, "Alpha must be between"),
        (
            {
                "minimum_selected_claim_probability": None,
                "maximum_type_s": None,
                "maximum_type_m": None,
            },
            "At least one precision guardrail",
        ),
        ({"minimum_selected_claim_probability": 1.0}, "Minimum selected-claim"),
        ({"maximum_type_s": 0.0}, "Maximum Type S"),
        ({"maximum_type_m": 1.0}, "Maximum Type M"),
        ({"standard_error": 0.0}, "standard error must be positive"),
        (
            {"sensitivity_enabled": True, "sensitivity_min": None, "sensitivity_max": 1.0},
            "Sensitivity minimum and maximum",
        ),
        (
            {"sample_size_projection_enabled": True, "current_effective_n": 0.0},
            "effective sample size must be positive",
        ),
    ],
)
def test_request_validation_is_explicit(
    planning_payload: Callable[..., dict[str, object]],
    overrides: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ValidationError, match=message):
        _calculate(planning_payload(**overrides))


def test_request_schema_rejects_missing_extra_and_boolean_numbers(
    planning_payload: Callable[..., dict[str, object]],
) -> None:
    missing = planning_payload()
    del missing["alpha"]
    extra = planning_payload(extra=1)

    with pytest.raises(ValidationError, match="Missing required field: alpha"):
        PlanningRequest.from_mapping(missing)
    with pytest.raises(ValidationError, match="Unexpected field: extra"):
        PlanningRequest.from_mapping(extra)
    with pytest.raises(ValidationError, match="Alpha must be a number"):
        PlanningRequest.from_mapping(planning_payload(alpha=True))
