"""Typed browser models for inverse Wald precision guardrail planning."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Literal

type PrecisionMode = Literal["direct_se", "ci_95"]


class ValidationError(ValueError):
    """A user-correctable request error safe to show in the browser."""


def _finite_number(value: object, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValidationError(f"{field} must be a number.")
    number = float(value)
    if not math.isfinite(number):
        raise ValidationError(f"{field} must be finite.")
    return number


def _optional_finite_number(value: object, *, field: str) -> float | None:
    if value is None:
        return None
    return _finite_number(value, field=field)


def _required_string(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{field} must be a non-empty string.")
    return value


def _required_boolean(value: object, *, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValidationError(f"{field} must be true or false.")
    return value


@dataclass(frozen=True)
class PlanningRequest:
    """Validated controls for one inverse-precision planning scenario."""

    precision_mode: PrecisionMode
    effect_type: str
    standard_error: float | None
    ci_lower: float | None
    ci_upper: float | None
    null_value: float
    target_true_effect: float
    alpha: float
    selection_rule: str
    claim_direction: str
    claim_threshold: float | None
    minimum_selected_claim_probability: float | None
    maximum_type_s: float | None
    maximum_type_m: float | None
    sensitivity_enabled: bool
    sensitivity_min: float | None
    sensitivity_max: float | None
    sensitivity_points: int
    sample_size_projection_enabled: bool
    current_effective_n: float | None

    @classmethod
    def from_mapping(cls, payload: object) -> PlanningRequest:
        """Build a request from one strict, flat JSON object."""

        if not isinstance(payload, dict):
            raise ValidationError("Request must be a JSON object.")
        expected = {
            "alpha",
            "ci_lower",
            "ci_upper",
            "claim_direction",
            "claim_threshold",
            "current_effective_n",
            "effect_type",
            "maximum_type_m",
            "maximum_type_s",
            "minimum_selected_claim_probability",
            "null_value",
            "precision_mode",
            "sample_size_projection_enabled",
            "selection_rule",
            "sensitivity_enabled",
            "sensitivity_max",
            "sensitivity_min",
            "sensitivity_points",
            "standard_error",
            "target_true_effect",
        }
        unexpected = sorted(set(payload) - expected)
        missing = sorted(expected - set(payload))
        if missing:
            raise ValidationError(f"Missing required field: {missing[0]}.")
        if unexpected:
            raise ValidationError(f"Unexpected field: {unexpected[0]}.")

        precision_mode = _required_string(payload["precision_mode"], field="Precision mode")
        if precision_mode not in {"direct_se", "ci_95"}:
            raise ValidationError("Precision mode must be 'direct_se' or 'ci_95'.")
        sensitivity_points = payload["sensitivity_points"]
        if isinstance(sensitivity_points, bool) or not isinstance(sensitivity_points, int):
            raise ValidationError("Sensitivity points must be an integer.")

        return cls(
            precision_mode=precision_mode,
            effect_type=_required_string(payload["effect_type"], field="Effect measure"),
            standard_error=_optional_finite_number(
                payload["standard_error"],
                field="Working-scale standard error",
            ),
            ci_lower=_optional_finite_number(
                payload["ci_lower"],
                field="Lower 95% confidence limit",
            ),
            ci_upper=_optional_finite_number(
                payload["ci_upper"],
                field="Upper 95% confidence limit",
            ),
            null_value=_finite_number(payload["null_value"], field="Null value"),
            target_true_effect=_finite_number(
                payload["target_true_effect"],
                field="Assumed true effect",
            ),
            alpha=_finite_number(payload["alpha"], field="Alpha"),
            selection_rule=_required_string(
                payload["selection_rule"],
                field="Selected-claim rule",
            ),
            claim_direction=_required_string(
                payload["claim_direction"],
                field="Claim direction",
            ),
            claim_threshold=_optional_finite_number(
                payload["claim_threshold"],
                field="Claim threshold",
            ),
            minimum_selected_claim_probability=_optional_finite_number(
                payload["minimum_selected_claim_probability"],
                field="Minimum selected-claim probability",
            ),
            maximum_type_s=_optional_finite_number(
                payload["maximum_type_s"],
                field="Maximum Type S",
            ),
            maximum_type_m=_optional_finite_number(
                payload["maximum_type_m"],
                field="Maximum Type M",
            ),
            sensitivity_enabled=_required_boolean(
                payload["sensitivity_enabled"],
                field="Sensitivity enabled",
            ),
            sensitivity_min=_optional_finite_number(
                payload["sensitivity_min"],
                field="Sensitivity minimum",
            ),
            sensitivity_max=_optional_finite_number(
                payload["sensitivity_max"],
                field="Sensitivity maximum",
            ),
            sensitivity_points=sensitivity_points,
            sample_size_projection_enabled=_required_boolean(
                payload["sample_size_projection_enabled"],
                field="Sample-size projection enabled",
            ),
            current_effective_n=_optional_finite_number(
                payload["current_effective_n"],
                field="Current effective sample size",
            ),
        )


@dataclass(frozen=True)
class PlanningResponse:
    """Focused response without observed-evidence or full Type S/M panels."""

    meta: dict[str, Any]
    current_precision: dict[str, Any]
    assumptions: dict[str, Any]
    selection_rule: dict[str, Any]
    target_effect: dict[str, Any]
    per_target_results: list[dict[str, Any]]
    joint_result: dict[str, Any]
    sensitivity_optional: dict[str, Any] | None
    sample_size_projection_optional: dict[str, Any] | None
    warnings: list[str]

    def to_payload(self) -> dict[str, Any]:
        """Return the stable ten-part focused response contract."""

        return {
            "meta": self.meta,
            "current_precision": self.current_precision,
            "assumptions": self.assumptions,
            "selection_rule": self.selection_rule,
            "target_effect": self.target_effect,
            "per_target_results": self.per_target_results,
            "joint_result": self.joint_result,
            "sensitivity_optional": self.sensitivity_optional,
            "sample_size_projection_optional": self.sample_size_projection_optional,
            "warnings": self.warnings,
        }
