export function filenameSlug(value) {
  const slug = value
    .normalize("NFKD")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80);
  return slug || "scientific-applet";
}

function csvCell(value) {
  const text = Array.isArray(value) ? value.join("|") : String(value ?? "");
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

export function csvFromRows(columns, rows) {
  const header = columns.map((column) => csvCell(column.label)).join(",");
  const records = rows.map((row) =>
    columns.map((column) => csvCell(row[column.key])).join(","),
  );
  return [header, ...records].join("\r\n") + "\r\n";
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

function dataUrlToBlob(dataUrl) {
  const [metadata, encoded] = dataUrl.split(",", 2);
  const mime =
    metadata.match(/^data:([^;]+);base64$/)?.[1] || "application/octet-stream";
  const bytes = Uint8Array.from(atob(encoded), (character) =>
    character.charCodeAt(0),
  );
  return new Blob([bytes], { type: mime });
}

function canvasBlob(canvas) {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) {
        resolve(blob);
      } else {
        reject(new Error("The browser could not create a PNG."));
      }
    }, "image/png");
  });
}

function loadImage(dataUrl) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.addEventListener("load", () => resolve(image), { once: true });
    image.addEventListener(
      "error",
      () => reject(new Error("Could not render the plot image.")),
      { once: true },
    );
    image.src = dataUrl;
  });
}

function drawWrappedText(context, text, x, y, maxWidth, lineHeight, maxLines) {
  const words = text.split(/\s+/);
  let line = "";
  let lineIndex = 0;
  for (const word of words) {
    const candidate = line ? `${line} ${word}` : word;
    if (context.measureText(candidate).width <= maxWidth) {
      line = candidate;
      continue;
    }
    context.fillText(line, x, y + lineIndex * lineHeight);
    lineIndex += 1;
    if (lineIndex >= maxLines) {
      return;
    }
    line = word;
  }
  if (line && lineIndex < maxLines) {
    context.fillText(line, x, y + lineIndex * lineHeight);
  }
}

const RESULT_COLUMNS = [
  { key: "row_kind", label: "row_kind" },
  { key: "effect_type", label: "effect_type" },
  { key: "assumed_true_effect_display", label: "assumed_true_effect_display" },
  { key: "assumed_true_effect_working", label: "assumed_true_effect_working" },
  { key: "current_se_working", label: "current_se_working" },
  { key: "selection_rule", label: "selection_rule" },
  { key: "alpha", label: "alpha" },
  { key: "claim_direction", label: "claim_direction" },
  { key: "claim_threshold_display", label: "claim_threshold_display" },
  { key: "target_name", label: "target_name" },
  { key: "requested_value", label: "requested_value" },
  { key: "status", label: "status" },
  { key: "required_se_working", label: "required_se_working" },
  {
    key: "required_information_multiplier",
    label: "required_information_multiplier",
  },
  {
    key: "approx_95_ci_width_working",
    label: "approx_95_ci_width_working",
  },
  {
    key: "achieved_selected_claim_probability",
    label: "achieved_selected_claim_probability",
  },
  { key: "achieved_type_s", label: "achieved_type_s" },
  { key: "achieved_type_m", label: "achieved_type_m" },
  { key: "binding_targets", label: "binding_targets" },
  {
    key: "current_precision_sufficient",
    label: "current_precision_sufficient",
  },
  { key: "note", label: "note" },
];

function context(response) {
  return {
    alpha: response.selection_rule.alpha,
    assumed_true_effect_display:
      response.target_effect.assumed_true_effect_display,
    assumed_true_effect_working:
      response.target_effect.assumed_true_effect_working,
    claim_direction: response.selection_rule.claim_direction,
    claim_threshold_display: response.selection_rule.claim_threshold_display,
    current_se_working: response.current_precision.current_se_working,
    effect_type: response.meta.effect_type,
    selection_rule: response.selection_rule.key,
  };
}

export function scenarioRows(response) {
  const shared = context(response);
  const rows = response.per_target_results.map((target) => ({
    ...shared,
    achieved_selected_claim_probability:
      target.achieved_selected_claim_probability,
    achieved_type_m: target.achieved_type_m,
    achieved_type_s: target.achieved_type_s,
    approx_95_ci_width_working: target.approx_95_ci_width_working,
    binding_targets: [],
    current_precision_sufficient: target.current_precision_sufficient,
    note: target.solver_note,
    requested_value: target.requested_value,
    required_information_multiplier: target.required_information_multiplier,
    required_se_working: target.required_se_working,
    row_kind: "target",
    status: target.status,
    target_name: target.target_name,
  }));
  rows.push({
    ...shared,
    achieved_selected_claim_probability:
      response.joint_result.achieved_selected_claim_probability,
    achieved_type_m: response.joint_result.achieved_type_m,
    achieved_type_s: response.joint_result.achieved_type_s,
    approx_95_ci_width_working:
      response.joint_result.approx_95_ci_width_working,
    binding_targets: response.joint_result.binding_targets,
    current_precision_sufficient:
      response.joint_result.current_precision_sufficient,
    note: response.joint_result.note,
    requested_value: null,
    required_information_multiplier:
      response.joint_result.required_information_multiplier,
    required_se_working: response.joint_result.required_se_working,
    row_kind: "joint",
    status: response.joint_result.status,
    target_name: "Joint mandatory requirement",
  });
  return rows;
}

export function sensitivityRows(response) {
  const sensitivity = response.sensitivity_optional;
  if (sensitivity === null) {
    return [];
  }
  const rows = [];
  for (const scenario of sensitivity.rows) {
    const shared = {
      ...context(response),
      assumed_true_effect_display: scenario.true_effect_display,
      assumed_true_effect_working: scenario.true_effect_working,
    };
    for (const target of scenario.target_results) {
      rows.push({
        ...shared,
        achieved_selected_claim_probability:
          target.achieved_selected_claim_probability,
        achieved_type_m: target.achieved_type_m,
        achieved_type_s: target.achieved_type_s,
        approx_95_ci_width_working: target.approx_95_ci_width_working,
        binding_targets: [],
        current_precision_sufficient: target.current_precision_sufficient,
        note: target.solver_note,
        requested_value: target.requested_value,
        required_information_multiplier: target.required_information_multiplier,
        required_se_working: target.required_se_working,
        row_kind: "sensitivity_target",
        status: target.status,
        target_name: target.target_name,
      });
    }
    rows.push({
      ...shared,
      achieved_selected_claim_probability: null,
      achieved_type_m: null,
      achieved_type_s: null,
      approx_95_ci_width_working: null,
      binding_targets: scenario.binding_targets,
      current_precision_sufficient: scenario.current_precision_sufficient,
      note: scenario.joint_note,
      requested_value: null,
      required_information_multiplier:
        scenario.joint_required_information_multiplier,
      required_se_working: scenario.joint_required_se_working,
      row_kind: "sensitivity_joint",
      status: scenario.joint_feasible ? "feasible" : "no_finite_joint_solution",
      target_name: "Joint mandatory requirement",
    });
  }
  return rows;
}

export function exportScenarioCsv(response, appTitle) {
  const csv = csvFromRows(RESULT_COLUMNS, scenarioRows(response));
  downloadBlob(
    new Blob([csv], { type: "text/csv;charset=utf-8" }),
    `${filenameSlug(appTitle)}-scenario-targets.csv`,
  );
}

export function exportSensitivityCsv(response, appTitle) {
  const rows = sensitivityRows(response);
  if (rows.length === 0) {
    throw new Error("Run a sensitivity analysis before exporting sensitivity CSV.");
  }
  const csv = csvFromRows(RESULT_COLUMNS, rows);
  downloadBlob(
    new Blob([csv], { type: "text/csv;charset=utf-8" }),
    `${filenameSlug(appTitle)}-sensitivity.csv`,
  );
}

export async function exportFigurePng(plotElement, appTitle) {
  const dataUrl = await globalThis.Plotly.toImage(plotElement, {
    format: "png",
    height: 1200,
    scale: 1,
    width: 1600,
  });
  downloadBlob(dataUrlToBlob(dataUrl), `${filenameSlug(appTitle)}-figure.png`);
}

export async function exportDashboardPng(plotElement, summary, appTitle) {
  const plotDataUrl = await globalThis.Plotly.toImage(plotElement, {
    format: "png",
    height: 820,
    scale: 1,
    width: 1200,
  });
  const plotImage = await loadImage(plotDataUrl);
  const canvas = document.createElement("canvas");
  canvas.width = 1400;
  canvas.height = 1180;
  const context = canvas.getContext("2d");
  context.fillStyle = "#ffffff";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "#17202a";
  context.font = "700 42px system-ui";
  context.fillText(appTitle, 80, 80, 1240);
  context.font = "24px system-ui";
  drawWrappedText(context, summary, 80, 135, 1240, 34, 4);
  context.drawImage(plotImage, 100, 290, 1200, 820);
  const blob = await canvasBlob(canvas);
  downloadBlob(blob, `${filenameSlug(appTitle)}-summary.png`);
}

export async function copyText(text) {
  await navigator.clipboard.writeText(text);
}
