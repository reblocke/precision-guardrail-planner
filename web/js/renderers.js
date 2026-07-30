function formatNumber(value) {
  if (value === null || value === undefined) {
    return "—";
  }
  return Number(value).toLocaleString("en-US", {
    maximumSignificantDigits: 8,
  });
}

function metric(label, value) {
  const term = document.createElement("dt");
  term.textContent = label;
  const detail = document.createElement("dd");
  detail.textContent = value;
  return [term, detail];
}

function renderJoint(response, elements) {
  const joint = response.joint_result;
  elements.jointCard.dataset.status = joint.feasible ? "feasible" : "infeasible";
  elements.jointStatus.textContent = joint.feasible
    ? joint.current_precision_sufficient
      ? "Current precision already satisfies every mandatory guardrail."
      : "A finite joint precision requirement is available."
    : "No finite joint solution exists under the selected assumptions.";
  elements.jointMetrics.replaceChildren();
  const rows = [
    ["Status", joint.status.replaceAll("_", " ")],
    ["Required working-scale SE", formatNumber(joint.required_se_working)],
    [
      "Required information multiplier",
      formatNumber(joint.required_information_multiplier),
    ],
    [
      "Approximate 95% working-scale CI width",
      formatNumber(joint.approx_95_ci_width_working),
    ],
    [
      "Binding target(s)",
      joint.binding_targets.length > 0 ? joint.binding_targets.join("; ") : "None",
    ],
  ];
  for (const [label, value] of rows) {
    elements.jointMetrics.append(...metric(label, value));
  }
  elements.jointNote.textContent = joint.note;
}

function renderTargetTable(response, table) {
  const body = table.querySelector("tbody");
  body.replaceChildren();
  for (const result of response.per_target_results) {
    const row = document.createElement("tr");
    row.dataset.status = result.status;
    const cells = [
      result.target_name,
      formatNumber(result.requested_value),
      result.status,
      formatNumber(result.required_se_working),
      formatNumber(result.required_information_multiplier),
      formatNumber(result.approx_95_ci_width_working),
      formatNumber(result.achieved_selected_claim_probability),
      formatNumber(result.achieved_type_s),
      formatNumber(result.achieved_type_m),
      result.solver_note,
    ];
    cells.forEach((value, index) => {
      const cell = document.createElement(index === 0 ? "th" : "td");
      if (index === 0) {
        cell.scope = "row";
      }
      cell.textContent = value;
      row.append(cell);
    });
    body.append(row);
  }
}

function renderSensitivityTable(response, elements) {
  const sensitivity = response.sensitivity_optional;
  elements.sensitivitySection.hidden = sensitivity === null;
  if (sensitivity === null) {
    return;
  }
  elements.sensitivityNote.textContent = sensitivity.note;
  const body = elements.sensitivityTable.querySelector("tbody");
  body.replaceChildren();
  for (const result of sensitivity.rows) {
    const row = document.createElement("tr");
    row.dataset.status = result.joint_feasible ? "feasible" : "infeasible";
    const cells = [
      formatNumber(result.true_effect_display),
      result.joint_feasible ? "feasible" : "no finite joint solution",
      formatNumber(result.joint_required_information_multiplier),
      formatNumber(result.joint_required_se_working),
      result.binding_targets.join("; ") || "None",
    ];
    for (const value of cells) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    }
    body.append(row);
  }
}

function renderProjection(response, elements) {
  const projection = response.sample_size_projection_optional;
  elements.sampleSizeSection.hidden = projection === null;
  if (projection === null) {
    return;
  }
  elements.sampleSizeResult.textContent =
    projection.approx_required_n === null
      ? projection.note
      : `Approximate required n: ${formatNumber(projection.approx_required_n)}. ` +
        projection.note;
}

function renderWarnings(response, list) {
  list.replaceChildren();
  for (const warning of response.warnings) {
    const item = document.createElement("li");
    item.textContent = warning;
    list.append(item);
  }
}

function sensitivityTraces(response) {
  const rows = response.sensitivity_optional.rows;
  const targetNames = response.per_target_results.map((row) => row.target_name);
  const chartName = (targetName) =>
    targetName === "Minimum selected-claim probability"
      ? "Claim probability"
      : targetName.replace("Maximum", "Max");
  const colors = ["#176b78", "#a84c00", "#513a83"];
  const traces = targetNames.map((targetName, targetIndex) => ({
    connectgaps: false,
    hovertemplate: "%{x:.6g}<br>%{y:.6g}x<extra>%{fullData.name}</extra>",
    line: { color: colors[targetIndex], dash: "dot", width: 2 },
    marker: { color: colors[targetIndex], size: 6 },
    mode: "lines+markers",
    name: chartName(targetName),
    type: "scatter",
    x: rows.map((row) => row.true_effect_display),
    y: rows.map((row) => {
      const target = row.target_results.find(
        (candidate) => candidate.target_name === targetName,
      );
      return target?.required_information_multiplier ?? null;
    }),
  }));
  traces.push({
    connectgaps: false,
    hovertemplate: "%{x:.6g}<br>%{y:.6g}x<extra>Joint envelope</extra>",
    line: { color: "#17202a", width: 4 },
    marker: { color: "#17202a", size: 7, symbol: "diamond" },
    mode: "lines+markers",
    name: "Joint",
    type: "scatter",
    x: rows.map((row) => row.true_effect_display),
    y: rows.map((row) => row.joint_required_information_multiplier),
  });
  return traces;
}

function scenarioTraces(response) {
  const labels = response.per_target_results.map((row) =>
    row.target_name === "Minimum selected-claim probability"
      ? "Claim probability"
      : row.target_name.replace("Maximum", "Max"),
  );
  const values = response.per_target_results.map(
    (row) => row.required_information_multiplier,
  );
  labels.push("Joint");
  values.push(response.joint_result.required_information_multiplier);
  return [
    {
      hovertemplate: "%{y}<br>%{x:.6g}x<extra></extra>",
      marker: {
        color: ["#176b78", "#a84c00", "#513a83", "#17202a"].slice(
          0,
          values.length,
        ),
      },
      name: "Required information",
      orientation: "h",
      type: "bar",
      x: values,
      y: labels,
    },
  ];
}

function figureLayout(response) {
  const sensitivity = response.sensitivity_optional;
  const values =
    sensitivity === null
      ? response.per_target_results
          .map((row) => row.required_information_multiplier)
          .filter((value) => value !== null)
      : sensitivity.rows
          .flatMap((row) => [
            row.joint_required_information_multiplier,
            ...row.target_results.map(
              (target) => target.required_information_multiplier,
            ),
          ])
          .filter((value) => value !== null);
  const positive = values.filter((value) => value > 0);
  const ratio =
    positive.length === 0 ? 1 : Math.max(...positive) / Math.min(...positive);
  const useLog = ratio >= 20;
  const shapes = [];
  if (sensitivity !== null) {
    shapes.push({
      line: { color: "#68777d", dash: "dash", width: 1.5 },
      type: "line",
      x0: response.target_effect.null_display,
      x1: response.target_effect.null_display,
      y0: 0,
      y1: 1,
      yref: "paper",
    });
    if (response.selection_rule.claim_threshold_display !== null) {
      shapes.push({
        line: { color: "#8b5f36", dash: "dot", width: 1.5 },
        type: "line",
        x0: response.selection_rule.claim_threshold_display,
        x1: response.selection_rule.claim_threshold_display,
        y0: 0,
        y1: 1,
        yref: "paper",
      });
    }
  }
  return {
    annotations: [],
    autosize: true,
    bargap: 0.28,
    height: 560,
    legend: { orientation: "h", x: 0, y: -0.3 },
    margin: {
      b: sensitivity === null ? 76 : 160,
      l: 70,
      r: 24,
      t: 76,
    },
    paper_bgcolor: "#ffffff",
    plot_bgcolor: "#ffffff",
    shapes,
    showlegend: sensitivity !== null,
    title: {
      text:
        sensitivity === null
          ? "Required information"
          : "Information across assumed effects",
      x: 0.5,
    },
    xaxis:
      sensitivity === null
        ? {
            gridcolor: "#dce3e5",
            rangemode: "tozero",
            title: { text: "Information multiplier" },
            type: "linear",
          }
        : {
            gridcolor: "#dce3e5",
            title: {
              text: `Assumed true ${response.meta.effect_label.toLowerCase()}`,
            },
            type: response.meta.effect_family === "ratio" ? "log" : undefined,
          },
    yaxis:
      sensitivity === null
        ? {
            automargin: true,
            autorange: "reversed",
            title: { text: "Guardrail" },
          }
        : {
            gridcolor: "#dce3e5",
            dtick: useLog ? 1 : undefined,
            rangemode: useLog ? undefined : "tozero",
            title: { text: "Information multiplier" },
            type: useLog ? "log" : "linear",
          },
  };
}

export async function renderResult(response, elements) {
  elements.summary.textContent = response.joint_result.feasible
    ? response.joint_result.current_precision_sufficient
      ? "Current precision already satisfies all mandatory guardrails; joint multiplier 1.0."
      : `Joint requirement: ${formatNumber(
          response.joint_result.required_information_multiplier,
        )}x current information.`
    : "No finite joint solution under the selected assumptions; per-target results are preserved.";
  elements.conditioning.textContent = response.assumptions.conditioning_statement;
  renderJoint(response, elements);
  renderTargetTable(response, elements.targetTable);
  renderSensitivityTable(response, elements);
  renderProjection(response, elements);
  renderWarnings(response, elements.warnings);
  elements.reviewerText.value = response.joint_result.reviewer_text;
  elements.caption.textContent =
    response.sensitivity_optional === null
      ? "Required relative information at the entered assumed true effect. Bars show each mandatory guardrail and the strictest joint requirement; missing bars indicate no finite solution."
      : "Required relative information across user-specified assumed true effects. Dotted colored lines show each mandatory guardrail, the solid black line shows the joint envelope, vertical markers show the null and active claim threshold, and gaps indicate no finite solution. The range is a sensitivity analysis, not a probability distribution.";

  if (!globalThis.Plotly) {
    throw new Error("The plotting library did not load.");
  }
  await globalThis.Plotly.react(
    elements.plot,
    response.sensitivity_optional === null
      ? scenarioTraces(response)
      : sensitivityTraces(response),
    figureLayout(response),
    {
      displaylogo: false,
      responsive: true,
      scrollZoom: false,
    },
  );
}
