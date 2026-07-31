"""Strict JSON boundary for inverse Wald precision guardrail planning."""

from __future__ import annotations

import json
import math
from dataclasses import asdict
from typing import Any

import wald_inference
from wald_inference import (
    approximate_wald_ci_width,
    get_effect_spec,
    joint_precision_result,
    precision_sensitivity,
    reconstruct_wald_from_95_ci,
    selection_rule_spec,
    to_working_scale,
)

from .models import PlanningRequest, PlanningResponse, ValidationError
from .version import __version__

ALL_SELECTION_RULES = (
    "two_sided_p_lt_alpha",
    "one_sided_positive_p_lt_alpha",
    "one_sided_negative_p_lt_alpha",
    "ci_excludes_null_in_beneficial_direction",
    "estimate_exceeds_mcid_and_p_lt_alpha",
    "ci_excludes_mcid",
)
RULES_REQUIRING_THRESHOLD = {
    "estimate_exceeds_mcid_and_p_lt_alpha",
    "ci_excludes_mcid",
}
RULES_USING_DIRECTION = {
    "ci_excludes_null_in_beneficial_direction",
    "estimate_exceeds_mcid_and_p_lt_alpha",
    "ci_excludes_mcid",
}
TARGET_LABELS = {
    "Power": "Minimum selected-claim probability",
    "Maximum Type S": "Maximum Type S",
    "Maximum Type M": "Maximum Type M",
}
BINDING_RELATIVE_TOLERANCE = 1e-8
MAX_SAFE_INTEGER = 9_007_199_254_740_991
MIN_SENSITIVITY_POINTS = 3
MAX_SENSITIVITY_POINTS = 101


def _reject_nonstandard_constant(value: str) -> None:
    raise ValidationError(f"Non-finite JSON constant is not allowed: {value}.")


def _call_core(function, /, *args, **kwargs):
    """Translate the released core's user-facing errors to this app boundary."""

    try:
        return function(*args, **kwargs)
    except wald_inference.ValidationError as exc:
        raise ValidationError(str(exc)) from exc


def _working_value(effect_type: str, value: float) -> float:
    return float(_call_core(to_working_scale, effect_type, value))


def _validate_request_semantics(request: PlanningRequest) -> None:
    if request.selection_rule not in ALL_SELECTION_RULES:
        valid = ", ".join(ALL_SELECTION_RULES)
        raise ValidationError(f"Unsupported selected-claim rule. Expected one of: {valid}.")
    if request.claim_direction not in {"positive", "negative"}:
        raise ValidationError("Claim direction must be 'positive' or 'negative'.")
    if not 0 < request.alpha < 1:
        raise ValidationError("Alpha must be between 0 and 1.")

    needs_threshold = request.selection_rule in RULES_REQUIRING_THRESHOLD
    if needs_threshold and request.claim_threshold is None:
        raise ValidationError("Claim threshold is required for the selected rule.")
    if not needs_threshold and request.claim_threshold is not None:
        raise ValidationError("Claim threshold must be blank for the selected rule.")

    if request.precision_mode == "direct_se":
        if request.standard_error is None or request.standard_error <= 0:
            raise ValidationError(
                "Working-scale standard error must be positive in direct-SE mode."
            )
        if request.ci_lower is not None or request.ci_upper is not None:
            raise ValidationError("Confidence limits must be blank in direct-SE mode.")
    else:
        if request.standard_error is not None:
            raise ValidationError("Working-scale standard error must be blank in CI mode.")
        if request.ci_lower is None or request.ci_upper is None:
            raise ValidationError("Both 95% confidence limits are required in CI mode.")

    targets = (
        request.minimum_selected_claim_probability,
        request.maximum_type_s,
        request.maximum_type_m,
    )
    if all(target is None for target in targets):
        raise ValidationError("At least one precision guardrail is required.")
    if (
        request.minimum_selected_claim_probability is not None
        and not 0 < request.minimum_selected_claim_probability < 1
    ):
        raise ValidationError("Minimum selected-claim probability must be between 0 and 1.")
    if request.maximum_type_s is not None and not 0 < request.maximum_type_s < 1:
        raise ValidationError("Maximum Type S must be between 0 and 1.")
    if request.maximum_type_m is not None and request.maximum_type_m <= 1:
        raise ValidationError("Maximum Type M must be greater than 1.")

    sensitivity_pair = (request.sensitivity_min, request.sensitivity_max)
    if request.sensitivity_enabled:
        if None in sensitivity_pair:
            raise ValidationError(
                "Sensitivity minimum and maximum are required when sensitivity is enabled."
            )
        assert sensitivity_pair[0] is not None and sensitivity_pair[1] is not None
        if sensitivity_pair[0] >= sensitivity_pair[1]:
            raise ValidationError("Sensitivity minimum must be less than the maximum.")
        if not MIN_SENSITIVITY_POINTS <= request.sensitivity_points <= MAX_SENSITIVITY_POINTS:
            raise ValidationError(
                f"Sensitivity points must be between {MIN_SENSITIVITY_POINTS} "
                f"and {MAX_SENSITIVITY_POINTS}."
            )
    elif any(value is not None for value in sensitivity_pair):
        raise ValidationError("Sensitivity bounds must be blank when sensitivity is disabled.")

    if request.sample_size_projection_enabled:
        if request.current_effective_n is None or request.current_effective_n <= 0:
            raise ValidationError(
                "Current effective sample size must be positive when projection is enabled."
            )
        if request.current_effective_n > MAX_SAFE_INTEGER:
            raise ValidationError(
                "Current effective sample size exceeds the browser-safe integer range."
            )
    elif request.current_effective_n is not None:
        raise ValidationError(
            "Current effective sample size must be blank unless projection is explicitly enabled."
        )


def _current_precision(
    request: PlanningRequest,
    *,
    effect_spec,
) -> tuple[dict[str, Any], float, list[str]]:
    warnings: list[str] = []
    if request.precision_mode == "direct_se":
        assert request.standard_error is not None
        current_se = request.standard_error
        ci_details: dict[str, Any] = {
            "ci_lower_display": None,
            "ci_upper_display": None,
            "ci_implied_midpoint_display": None,
            "ci_reconstruction_method": None,
            "ci_relative_asymmetry": None,
        }
        source_note = (
            "The entered SE is interpreted on the log working scale."
            if effect_spec.family == "ratio"
            else "The entered SE is interpreted on the additive identity working scale."
        )
    else:
        assert request.ci_lower is not None and request.ci_upper is not None
        reconstruction = _call_core(
            reconstruct_wald_from_95_ci,
            effect_type=request.effect_type,
            lower=request.ci_lower,
            upper=request.ci_upper,
            null_value=request.null_value,
        )
        current_se = float(reconstruction.standard_error)
        ci_details = {
            "ci_lower_display": reconstruction.lower_display,
            "ci_upper_display": reconstruction.upper_display,
            "ci_implied_midpoint_display": reconstruction.estimate_display,
            "ci_reconstruction_method": reconstruction.se_method,
            "ci_relative_asymmetry": reconstruction.relative_asymmetry,
        }
        warnings.extend(reconstruction.warnings)
        source_note = (
            "The reported 95% CI reconstructs current working-scale precision only. "
            "Its midpoint is not treated as the assumed truth."
        )

    return (
        {
            "mode": request.precision_mode,
            "current_se_working": current_se,
            "approx_95_ci_width_working": float(_call_core(approximate_wald_ci_width, current_se)),
            **ci_details,
            "source_note": source_note,
        },
        current_se,
        warnings,
    )


def _target_row(row) -> dict[str, Any]:
    payload = asdict(row)
    solver_note = row.note.replace(
        "Current CI-implied precision",
        "Current precision",
    )
    return {
        "target_key": row.target,
        "target_name": TARGET_LABELS[row.target],
        "requested_value": row.requested_value,
        "status": "feasible" if row.feasible else "infeasible",
        "feasible": row.feasible,
        "current_precision_sufficient": row.current_precision_sufficient,
        "required_se_working": row.required_se,
        "required_information_multiplier": row.required_information_multiplier,
        "approx_95_ci_width_working": row.approx_95_ci_width_working,
        "achieved_selected_claim_probability": payload["achieved_power"],
        "achieved_type_s": payload["achieved_type_s"],
        "achieved_type_m": payload["achieved_type_m"],
        "solver_note": solver_note,
    }


def _binding_labels(binding_targets: tuple[str, ...]) -> list[str]:
    return [TARGET_LABELS[target] for target in binding_targets]


def _reviewer_text(
    *,
    request: PlanningRequest,
    effect_label: str,
    current_se: float,
    rule_label: str,
    joint,
    sample_size_projection: dict[str, Any] | None,
) -> str:
    guardrails = "; ".join(
        f"{TARGET_LABELS[row.target]} {row.requested_value:g}" for row in joint.target_results
    )
    threshold_text = (
        ""
        if request.claim_threshold is None
        else f", and a claim threshold of {request.claim_threshold:g}"
    )
    opening = (
        f"Under a one-parameter Wald model, we conditioned precision planning on an assumed true "
        f"{effect_label.lower()} of {request.target_true_effect:g}, a {rule_label.lower()} "
        f"selected-claim rule at alpha {request.alpha:g} with "
        f"{request.claim_direction} claim direction{threshold_text}, and a current working-scale "
        f"SE of {current_se:.6g}. Mandatory guardrails were {guardrails}."
    )
    if not joint.feasible:
        result_text = (
            " No finite joint solution was available under these assumptions; the per-target "
            f"results identify each infeasible guardrail. {joint.note}"
        )
    else:
        assert joint.required_se is not None
        assert joint.required_information_multiplier is not None
        binding = ", ".join(_binding_labels(joint.binding_targets))
        result_text = (
            f" The joint requirement was a working-scale SE of {joint.required_se:.6g} "
            f"({joint.required_information_multiplier:.6g} times current information), with "
            f"{binding} binding within relative multiplier tolerance "
            f"{BINDING_RELATIVE_TOLERANCE:g}."
        )
    sample_text = ""
    if sample_size_projection is not None:
        projected = sample_size_projection["approx_required_n"]
        if projected is not None:
            sample_text = (
                f" Under the explicit assumption that information is proportional to sample "
                f"size and all other design features remain unchanged, the approximate projected "
                f"sample size is {projected} from a current effective sample size of "
                f"{request.current_effective_n:g}; this is not a design-specific calculation."
            )
    return (
        opening
        + result_text
        + sample_text
        + " Results depend on the assumed true effect, selected-claim rule, Wald approximation, "
        "and relative-information scaling; they do not replace a formal study-design analysis."
    )


def _sensitivity_values(request: PlanningRequest) -> list[float]:
    assert request.sensitivity_min is not None and request.sensitivity_max is not None
    span = request.sensitivity_max - request.sensitivity_min
    values = [
        request.sensitivity_min + span * index / (request.sensitivity_points - 1)
        for index in range(request.sensitivity_points)
    ]
    values[0] = request.sensitivity_min
    values[-1] = request.sensitivity_max
    if not all(math.isfinite(value) for value in values):
        raise ValidationError("Sensitivity range exceeds the finite numeric range.")
    return values


def _sample_size_projection(request: PlanningRequest, joint) -> dict[str, Any] | None:
    if not request.sample_size_projection_enabled:
        return None
    assert request.current_effective_n is not None
    projected: int | None = None
    note: str
    if joint.required_information_multiplier is None:
        note = (
            "No sample-size projection is available because the mandatory joint target has "
            "no finite solution under the selected assumptions."
        )
    else:
        raw_required = request.current_effective_n * joint.required_information_multiplier
        if not math.isfinite(raw_required) or raw_required > MAX_SAFE_INTEGER:
            raise ValidationError(
                "Approximate required sample size exceeds the browser-safe integer range."
            )
        projected = math.ceil(raw_required)
        note = (
            "Approximate only: ceil(current effective n × information multiplier). "
            "This assumes information is proportional to sample size and all other design "
            "features remain unchanged; it is not a design-specific sample-size calculation."
        )
    return {
        "enabled": True,
        "assumption_active": True,
        "current_effective_n": request.current_effective_n,
        "required_information_multiplier": joint.required_information_multiplier,
        "approx_required_n": projected,
        "note": note,
    }


def calculate(request: PlanningRequest) -> PlanningResponse:
    """Build the complete focused response using only released Core calculations."""

    _validate_request_semantics(request)
    effect_spec = _call_core(get_effect_spec, request.effect_type)
    current_precision, current_se, warnings = _current_precision(
        request,
        effect_spec=effect_spec,
    )
    null_working = _working_value(request.effect_type, request.null_value)
    true_effect_working = _working_value(request.effect_type, request.target_true_effect)
    threshold_working = (
        None
        if request.claim_threshold is None
        else _working_value(request.effect_type, request.claim_threshold)
    )
    rule = _call_core(
        selection_rule_spec,
        selection_rule=request.selection_rule,
        alpha=request.alpha,
        null_working=null_working,
        se=current_se,
        claim_direction=request.claim_direction,
        threshold_working=threshold_working,
    )
    core_kwargs = {
        "null_working": null_working,
        "current_se": current_se,
        "alpha": request.alpha,
        "target_power": request.minimum_selected_claim_probability,
        "max_type_s": request.maximum_type_s,
        "max_type_m": request.maximum_type_m,
        "selection_rule": request.selection_rule,
        "claim_direction": request.claim_direction,
        "threshold_working": threshold_working,
        "binding_relative_tolerance": BINDING_RELATIVE_TOLERANCE,
    }
    joint = _call_core(joint_precision_result, true_effect_working, **core_kwargs)
    per_target_results = [_target_row(row) for row in joint.target_results]
    sample_size_projection = _sample_size_projection(request, joint)

    sensitivity_optional: dict[str, Any] | None = None
    if request.sensitivity_enabled:
        display_values = _sensitivity_values(request)
        working_values = [_working_value(request.effect_type, value) for value in display_values]
        sensitivity_results = _call_core(
            precision_sensitivity,
            working_values,
            **core_kwargs,
        )
        sensitivity_optional = {
            "enabled": True,
            "grid_scale": "natural_display_linear",
            "range_is_distribution": False,
            "rows": [
                {
                    "true_effect_display": display_value,
                    "true_effect_working": result.true_effect_working,
                    "joint_feasible": result.feasible,
                    "joint_required_se_working": result.required_se,
                    "joint_required_information_multiplier": (
                        result.required_information_multiplier
                    ),
                    "binding_targets": _binding_labels(result.binding_targets),
                    "current_precision_sufficient": result.current_precision_sufficient,
                    "joint_note": result.note,
                    "target_results": [_target_row(row) for row in result.target_results],
                }
                for display_value, result in zip(
                    display_values,
                    sensitivity_results,
                    strict=True,
                )
            ],
            "note": (
                "The range is a user-specified sensitivity analysis, not a probability "
                "distribution or posterior for the true effect."
            ),
        }

    binding_labels = _binding_labels(joint.binding_targets)
    joint_result = {
        "status": "feasible" if joint.feasible else "no_finite_joint_solution",
        "feasible": joint.feasible,
        "required_se_working": joint.required_se,
        "required_information_multiplier": joint.required_information_multiplier,
        "approx_95_ci_width_working": joint.approx_95_ci_width_working,
        "binding_targets": binding_labels,
        "binding_relative_tolerance": BINDING_RELATIVE_TOLERANCE,
        "current_precision_sufficient": joint.current_precision_sufficient,
        "achieved_selected_claim_probability": (joint.achieved_selected_claim_probability),
        "achieved_type_s": joint.achieved_type_s,
        "achieved_type_m": joint.achieved_type_m,
        "note": joint.note,
        "reviewer_text": "",
    }
    joint_result["reviewer_text"] = _reviewer_text(
        request=request,
        effect_label=effect_spec.label,
        current_se=current_se,
        rule_label=rule.label,
        joint=joint,
        sample_size_projection=sample_size_projection,
    )

    if not joint.feasible:
        warnings.append(joint.note)
    for row in per_target_results:
        if not row["feasible"]:
            warnings.append(f"{row['target_name']} is infeasible: {row['solver_note']}")
    if effect_spec.family == "ratio":
        warnings.append(
            "Ratio effects are converted to the log working scale. Type M and precision "
            "distances are defined on that log scale."
        )
    if request.sensitivity_enabled:
        warnings.append(
            "The plausible true-effect range is a sensitivity range, not a posterior distribution."
        )
    warnings.append(
        "Information multipliers are relative-information requirements, not automatically "
        "sample-size multipliers."
    )

    working_scale_note = (
        "Natural-scale ratio inputs are converted to the log working scale."
        if effect_spec.family == "ratio"
        else "Additive inputs use their identity working scale."
    )
    assumptions = {
        "wald_model": "One-parameter normal/Wald repeated-study model.",
        "conditioning_statement": (
            f"All results condition on the assumed true {effect_spec.label.lower()} "
            f"{request.target_true_effect:g}; the app does not estimate a distribution of "
            "true effects."
        ),
        "selected_claim_rule_dependence": (
            "Selected-claim probability, Type S, Type M, feasibility, and required "
            "information depend on the active claim rule and alpha."
        ),
        "information_scaling": (
            "Core defines multiplier M by required SE = current SE / sqrt(M); M is relative "
            "information, not automatically sample size."
        ),
        "working_scale": working_scale_note,
        "sample_size_projection_active": request.sample_size_projection_enabled,
    }
    active_controls = ["alpha"]
    if request.selection_rule in RULES_USING_DIRECTION:
        active_controls.append("claim direction")
    if request.selection_rule in RULES_REQUIRING_THRESHOLD:
        active_controls.append("claim threshold")

    return PlanningResponse(
        meta={
            "schema_version": 1,
            "app_version": __version__,
            "core_version": wald_inference.__version__,
            "effect_type": effect_spec.key,
            "effect_label": effect_spec.label,
            "effect_family": effect_spec.family,
            "working_scale": effect_spec.working_scale,
            "question": (
                "What working-scale precision and relative information are required to meet "
                "the selected mandatory guardrails?"
            ),
            "numerical_authority": (
                "wald-inference 0.4.2 joint_precision_result and precision_sensitivity"
            ),
            "scope": "inverse_precision_guardrails_only",
        },
        current_precision=current_precision,
        assumptions=assumptions,
        selection_rule={
            "key": rule.key,
            "label": rule.label,
            "alpha": rule.alpha,
            "claim_direction": request.claim_direction,
            "claim_threshold_display": request.claim_threshold,
            "claim_threshold_working": threshold_working,
            "active_controls": active_controls,
        },
        target_effect={
            "assumed_true_effect_display": request.target_true_effect,
            "assumed_true_effect_working": true_effect_working,
            "null_display": request.null_value,
            "null_working": null_working,
            "distance_from_null_working": true_effect_working - null_working,
            "conditioning_note": assumptions["conditioning_statement"],
        },
        per_target_results=per_target_results,
        joint_result=joint_result,
        sensitivity_optional=sensitivity_optional,
        sample_size_projection_optional=sample_size_projection,
        warnings=warnings,
    )


def calculate_json(request_json: str) -> str:
    """Validate a strict JSON request and return strict JSON."""

    try:
        payload = json.loads(request_json, parse_constant=_reject_nonstandard_constant)
    except json.JSONDecodeError as exc:
        raise ValidationError("Request must be valid JSON.") from exc
    response = calculate(PlanningRequest.from_mapping(payload))
    return json.dumps(
        response.to_payload(),
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
