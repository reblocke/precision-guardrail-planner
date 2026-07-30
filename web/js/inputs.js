const THRESHOLD_RULES = new Set([
  "estimate_exceeds_mcid_and_p_lt_alpha",
  "ci_excludes_mcid",
]);

const EFFECT_DEFAULTS = {
  additive: {
    claim_threshold: "0.1",
    null_value: "0",
    sensitivity_max: "0.5",
    sensitivity_min: "-0.1",
    target_true_effect: "0.2",
  },
  ratio: {
    claim_threshold: "1.2",
    null_value: "1",
    sensitivity_max: "2",
    sensitivity_min: "0.8",
    target_true_effect: "1.5",
  },
};

const RATIO_EFFECTS = new Set([
  "odds_ratio",
  "risk_ratio",
  "hazard_ratio",
  "incidence_rate_ratio",
  "ratio_of_means",
]);

function control(form, name) {
  return form.elements.namedItem(name);
}

function fieldError(element, message) {
  element.setAttribute("aria-invalid", "true");
  return { controlId: element.id, message };
}

function parseNumber(form, name, label, { integer = false, optional = false } = {}) {
  const element = control(form, name);
  const text = element.value.trim();
  if (text === "" && optional) {
    return { value: null };
  }
  if (text === "") {
    return { error: fieldError(element, `${label} is required.`) };
  }
  const value = Number(text);
  if (!Number.isFinite(value)) {
    return { error: fieldError(element, `${label} must be a finite number.`) };
  }
  if (integer && !Number.isInteger(value)) {
    return { error: fieldError(element, `${label} must be an integer.`) };
  }
  return { value };
}

function pushError(errors, parsed) {
  if (parsed.error) {
    errors.push(parsed.error);
  }
  return parsed.value;
}

export function applyEffectDefaults(form) {
  const effectType = control(form, "effect_type").value;
  const defaults = RATIO_EFFECTS.has(effectType)
    ? EFFECT_DEFAULTS.ratio
    : EFFECT_DEFAULTS.additive;
  for (const [name, value] of Object.entries(defaults)) {
    control(form, name).value = value;
  }
  const rule = control(form, "selection_rule").value;
  control(form, "claim_threshold").value = THRESHOLD_RULES.has(rule)
    ? defaults.claim_threshold
    : "";
}

export function updateControlState(form) {
  const precisionMode = control(form, "precision_mode").value;
  for (const container of form.querySelectorAll("[data-precision-control]")) {
    const active = container.dataset.precisionControl === precisionMode;
    container.hidden = !active;
    for (const element of container.querySelectorAll("input")) {
      element.disabled = !active;
    }
  }

  const thresholdActive = THRESHOLD_RULES.has(control(form, "selection_rule").value);
  const threshold = control(form, "claim_threshold");
  threshold.disabled = !thresholdActive;
  if (!thresholdActive) {
    threshold.value = "";
  } else if (threshold.value.trim() === "") {
    const effectType = control(form, "effect_type").value;
    threshold.value = RATIO_EFFECTS.has(effectType) ? "1.2" : "0.1";
  }

  const guardrails = [
    ["target_probability_enabled", "minimum_selected_claim_probability"],
    ["maximum_type_s_enabled", "maximum_type_s"],
    ["maximum_type_m_enabled", "maximum_type_m"],
  ];
  for (const [enabledName, valueName] of guardrails) {
    control(form, valueName).disabled = !control(form, enabledName).checked;
  }

  const sensitivityEnabled = control(form, "sensitivity_enabled").checked;
  for (const name of ["sensitivity_min", "sensitivity_max", "sensitivity_points"]) {
    control(form, name).disabled = !sensitivityEnabled;
  }
  control(form, "current_effective_n").disabled = !control(
    form,
    "sample_size_projection_enabled",
  ).checked;
}

export function readRequest(form) {
  const errors = [];
  const precisionMode = control(form, "precision_mode").value;
  const standardError =
    precisionMode === "direct_se"
      ? parseNumber(form, "standard_error", "Working-scale standard error")
      : { value: null };
  const ciLower =
    precisionMode === "ci_95"
      ? parseNumber(form, "ci_lower", "Lower 95% confidence limit")
      : { value: null };
  const ciUpper =
    precisionMode === "ci_95"
      ? parseNumber(form, "ci_upper", "Upper 95% confidence limit")
      : { value: null };
  const nullValue = parseNumber(form, "null_value", "Null value");
  const targetTrueEffect = parseNumber(
    form,
    "target_true_effect",
    "Assumed true effect",
  );
  const alpha = parseNumber(form, "alpha", "Alpha");

  const probabilityEnabled = control(form, "target_probability_enabled").checked;
  const typeSEnabled = control(form, "maximum_type_s_enabled").checked;
  const typeMEnabled = control(form, "maximum_type_m_enabled").checked;
  if (!probabilityEnabled && !typeSEnabled && !typeMEnabled) {
    errors.push(
      fieldError(
        control(form, "target_probability_enabled"),
        "Select at least one precision guardrail.",
      ),
    );
  }
  const targetProbability = probabilityEnabled
    ? parseNumber(
        form,
        "minimum_selected_claim_probability",
        "Minimum selected-claim probability",
      )
    : { value: null };
  const maximumTypeS = typeSEnabled
    ? parseNumber(form, "maximum_type_s", "Maximum Type S")
    : { value: null };
  const maximumTypeM = typeMEnabled
    ? parseNumber(form, "maximum_type_m", "Maximum Type M")
    : { value: null };

  const thresholdActive = THRESHOLD_RULES.has(control(form, "selection_rule").value);
  const claimThreshold = thresholdActive
    ? parseNumber(form, "claim_threshold", "Claim threshold")
    : { value: null };
  const sensitivityEnabled = control(form, "sensitivity_enabled").checked;
  const sensitivityMin = sensitivityEnabled
    ? parseNumber(form, "sensitivity_min", "Sensitivity minimum")
    : { value: null };
  const sensitivityMax = sensitivityEnabled
    ? parseNumber(form, "sensitivity_max", "Sensitivity maximum")
    : { value: null };
  const sensitivityPoints = sensitivityEnabled
    ? parseNumber(form, "sensitivity_points", "Sensitivity points", { integer: true })
    : { value: 19 };
  const sampleSizeEnabled = control(
    form,
    "sample_size_projection_enabled",
  ).checked;
  const currentEffectiveN = sampleSizeEnabled
    ? parseNumber(form, "current_effective_n", "Current effective sample size")
    : { value: null };

  const parsedValues = [
    standardError,
    ciLower,
    ciUpper,
    nullValue,
    targetTrueEffect,
    alpha,
    targetProbability,
    maximumTypeS,
    maximumTypeM,
    claimThreshold,
    sensitivityMin,
    sensitivityMax,
    sensitivityPoints,
    currentEffectiveN,
  ];
  for (const parsed of parsedValues) {
    if (parsed.error) {
      errors.push(parsed.error);
    }
  }
  if (errors.length > 0) {
    return { errors, request: null };
  }

  return {
    errors: [],
    request: {
      alpha: alpha.value,
      ci_lower: ciLower.value,
      ci_upper: ciUpper.value,
      claim_direction: control(form, "claim_direction").value,
      claim_threshold: claimThreshold.value,
      current_effective_n: currentEffectiveN.value,
      effect_type: control(form, "effect_type").value,
      maximum_type_m: maximumTypeM.value,
      maximum_type_s: maximumTypeS.value,
      minimum_selected_claim_probability: targetProbability.value,
      null_value: nullValue.value,
      precision_mode: precisionMode,
      sample_size_projection_enabled: sampleSizeEnabled,
      selection_rule: control(form, "selection_rule").value,
      sensitivity_enabled: sensitivityEnabled,
      sensitivity_max: sensitivityMax.value,
      sensitivity_min: sensitivityMin.value,
      sensitivity_points: sensitivityPoints.value,
      standard_error: standardError.value,
      target_true_effect: targetTrueEffect.value,
    },
  };
}
