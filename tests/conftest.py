from __future__ import annotations

from collections.abc import Callable

import pytest


@pytest.fixture
def planning_payload() -> Callable[..., dict[str, object]]:
    """Return the documented synthetic B06-style request with overrides."""

    def factory(**overrides: object) -> dict[str, object]:
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
        return payload

    return factory
