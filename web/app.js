import { clearFieldErrors, setStatus, showErrors } from "./js/accessibility.js";
import { APP_TITLE } from "./js/config.js";
import {
  copyText,
  exportDashboardPng,
  exportFigurePng,
  exportScenarioCsv,
  exportSensitivityCsv,
} from "./js/exports.js";
import {
  applyEffectDefaults,
  readRequest,
  updateControlState,
} from "./js/inputs.js";
import { renderResult } from "./js/renderers.js";
import { WorkerRuntime } from "./js/runtime.js";

const form = document.querySelector("#applet-form");
const errorSummary = document.querySelector("#error-summary");
const status = document.querySelector("#runtime-status");
const retryButton = document.querySelector("#retry-worker");
const calculateButton = document.querySelector("#calculate");
const result = document.querySelector("#result");
const emptyState = document.querySelector(".empty-state");
const plot = document.querySelector("#plot");
const exportButtons = [...document.querySelectorAll("[data-export]")];
const copyButtons = [...document.querySelectorAll("[data-copy]")];
const sensitivityExportButton = document.querySelector(
  "#export-sensitivity-csv",
);
const reviewerText = document.querySelector("#reviewer-text");
const runtime = new WorkerRuntime();
let currentResponse = null;
let calculationGeneration = 0;
let calculationInFlight = false;
let runtimeGeneration = 0;
let runtimeReady = false;

function resultElements() {
  return {
    caption: document.querySelector("#figure-caption"),
    conditioning: document.querySelector("#conditioning-result"),
    jointCard: document.querySelector("#joint-card"),
    jointMetrics: document.querySelector("#joint-metrics"),
    jointNote: document.querySelector("#joint-note"),
    jointStatus: document.querySelector("#joint-status"),
    plot,
    reviewerText,
    sampleSizeResult: document.querySelector("#sample-size-result"),
    sampleSizeSection: document.querySelector("#sample-size-section"),
    sensitivityNote: document.querySelector("#sensitivity-note"),
    sensitivitySection: document.querySelector("#sensitivity-section"),
    sensitivityTable: document.querySelector("#sensitivity-table"),
    summary: document.querySelector("#result-summary"),
    targetTable: document.querySelector("#target-table"),
    warnings: document.querySelector("#warnings-list"),
  };
}

function setExportAvailability(enabled) {
  for (const button of [...exportButtons, ...copyButtons]) {
    button.disabled = !enabled;
  }
  sensitivityExportButton.disabled =
    !enabled || currentResponse?.sensitivity_optional === null;
}

function clearResultState() {
  currentResponse = null;
  result.hidden = true;
  emptyState.hidden = false;
  setExportAvailability(false);
}

async function startRuntime() {
  const generation = ++runtimeGeneration;
  calculationGeneration += 1;
  calculationInFlight = false;
  runtimeReady = false;
  clearResultState();
  calculateButton.disabled = true;
  retryButton.hidden = true;
  setStatus(status, "Loading the local Python runtime…", "loading");
  try {
    const ready = await runtime.restart();
    if (generation !== runtimeGeneration) {
      return;
    }
    document.querySelector("#runtime-versions").textContent = ready.packages
      .map((entry) => `${entry.distribution} ${entry.version}`)
      .join(" · ");
    const core = ready.packages.find(
      (entry) => entry.distribution === "wald-inference",
    );
    document.querySelector("#core-version").textContent = core
      ? `Core: wald-inference ${core.version}`
      : "Core: unavailable";
    runtimeReady = true;
    calculateButton.disabled = false;
    setStatus(status, "Ready. Calculations stay in this browser.", "ready");
  } catch {
    if (generation !== runtimeGeneration) {
      return;
    }
    retryButton.hidden = false;
    setStatus(status, "The calculation worker could not start.", "error");
  }
}

form.addEventListener("change", (event) => {
  if (event.target.name === "effect_type") {
    applyEffectDefaults(form);
  }
  updateControlState(form);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const generation = ++calculationGeneration;
  clearResultState();
  clearFieldErrors(form);
  const { errors, request } = readRequest(form);
  showErrors(errorSummary, errors);
  if (errors.length > 0) {
    setStatus(status, "Check the highlighted inputs.", "error");
    return;
  }

  calculationInFlight = true;
  calculateButton.disabled = true;
  setStatus(status, "Planning precision…", "loading");
  try {
    const response = await runtime.calculate(request);
    if (generation !== calculationGeneration) {
      return;
    }
    emptyState.hidden = true;
    result.hidden = false;
    await renderResult(response, resultElements());
    if (generation !== calculationGeneration) {
      return;
    }
    currentResponse = response;
    setExportAvailability(true);
    setStatus(status, "Calculation complete.", "ready");
  } catch (error) {
    if (generation !== calculationGeneration) {
      return;
    }
    clearResultState();
    showErrors(errorSummary, [
      {
        controlId: null,
        message:
          error.code === "validation_error"
            ? error.message
            : "Calculation failed safely. Restart the worker and try again.",
      },
    ]);
    retryButton.hidden = error.code === "validation_error";
    setStatus(status, "Calculation failed.", "error");
  } finally {
    calculationInFlight = false;
    calculateButton.disabled = !runtimeReady;
    if (generation !== calculationGeneration && runtimeReady) {
      setStatus(status, "Ready. Calculations stay in this browser.", "ready");
    }
  }
});

form.addEventListener("reset", () => {
  calculationGeneration += 1;
  clearResultState();
  clearFieldErrors(form);
  showErrors(errorSummary, []);
  requestAnimationFrame(() => {
    updateControlState(form);
    calculateButton.disabled = calculationInFlight || !runtimeReady;
    setStatus(
      status,
      calculationInFlight
        ? "Reset complete. Discarding the in-flight result…"
        : "Ready. Calculations stay in this browser.",
      calculationInFlight ? "loading" : "ready",
    );
  });
});

retryButton.addEventListener("click", startRuntime);

document.querySelector("#export-scenario-csv").addEventListener("click", () => {
  exportScenarioCsv(currentResponse, APP_TITLE);
});
document.querySelector("#export-sensitivity-csv").addEventListener("click", () => {
  exportSensitivityCsv(currentResponse, APP_TITLE);
});
document.querySelector("#export-figure").addEventListener("click", async () => {
  await exportFigurePng(plot, APP_TITLE);
});
document.querySelector("#export-dashboard").addEventListener("click", async () => {
  const joint = currentResponse.joint_result;
  const summary =
    `${currentResponse.assumptions.conditioning_statement} ` +
    `Rule: ${currentResponse.selection_rule.label}; alpha ` +
    `${currentResponse.selection_rule.alpha}. ` +
    (joint.feasible
      ? `Joint information multiplier ${joint.required_information_multiplier}; ` +
        `binding: ${joint.binding_targets.join(", ")}.`
      : "No finite joint solution under the selected assumptions.");
  await exportDashboardPng(plot, summary, APP_TITLE);
});
document.querySelector("#copy-reviewer").addEventListener("click", async () => {
  await copyText(reviewerText.value);
  setStatus(status, "Reviewer text copied.", "ready");
});
document.querySelector("#copy-caption").addEventListener("click", async () => {
  await copyText(document.querySelector("#figure-caption").textContent);
  setStatus(status, "Figure caption copied.", "ready");
});

updateControlState(form);
setExportAvailability(false);
startRuntime();
