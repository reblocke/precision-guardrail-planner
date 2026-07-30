from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page, expect


def _ready(page: Page, app_url: str) -> None:
    page.goto(app_url)
    expect(page.locator("#runtime-status")).to_have_attribute(
        "data-state",
        "ready",
        timeout=120_000,
    )


def _calculate(page: Page) -> None:
    page.locator("#calculate").click()
    expect(page.locator("#runtime-status")).to_have_text(
        "Calculation complete.",
        timeout=120_000,
    )


def test_worker_loads_core_and_calculates_joint_requirement(
    page: Page,
    app_url: str,
) -> None:
    _ready(page, app_url)
    _calculate(page)

    expect(page.locator("#runtime-versions")).to_contain_text("wald-inference 0.4.1")
    expect(page.locator("#core-version")).to_have_text("wald-inference Core v0.4.1")
    expect(page.locator("#result-summary")).to_contain_text("4.908")
    expect(page.locator("#conditioning-result")).to_contain_text(
        "condition on the assumed true mean difference 0.2"
    )
    expect(page.locator("#joint-status")).to_contain_text("finite joint precision requirement")
    expect(page.locator("#target-table tbody tr")).to_have_count(3)
    expect(page.locator("#target-table tbody")).to_contain_text(
        "Minimum selected-claim probability"
    )
    expect(page.locator("#plot .plot-container")).to_be_visible()
    assert "binding" in page.locator("#reviewer-text").input_value()


def test_validation_error_is_safe_and_worker_recovers(
    page: Page,
    app_url: str,
) -> None:
    _ready(page, app_url)
    page.locator("#alpha").fill("0")
    page.locator("#calculate").click()

    expect(page.locator("#error-summary")).to_contain_text("Alpha must be between 0 and 1")
    expect(page.locator("#runtime-status")).to_have_attribute("data-state", "error")
    expect(page.locator("#error-summary")).not_to_contain_text("Traceback")
    expect(page.locator("#error-summary")).not_to_contain_text("/Users/")

    page.locator("#alpha").fill("0.05")
    _calculate(page)
    expect(page.locator("#result-summary")).to_contain_text("Joint requirement")


def test_input_errors_link_to_controls(page: Page, app_url: str) -> None:
    _ready(page, app_url)
    page.locator("#target-true-effect").fill("")
    page.locator("#calculate").click()

    expect(page.locator("#error-summary")).to_be_visible()
    expect(page.locator("#error-summary a")).to_have_attribute(
        "href",
        "#target-true-effect",
    )
    expect(page.locator("#target-true-effect")).to_have_attribute(
        "aria-invalid",
        "true",
    )


def test_sensitivity_csv_png_and_copy_exports(
    page: Page,
    app_url: str,
    tmp_path: Path,
) -> None:
    page.context.grant_permissions(
        ["clipboard-read", "clipboard-write"],
        origin=app_url.rstrip("/"),
    )
    _ready(page, app_url)
    page.get_by_text("Sensitivity across assumed true effects", exact=True).click()
    page.locator("#sensitivity-enabled").check()
    page.locator("#sensitivity-min").fill("0")
    page.locator("#sensitivity-max").fill("0.4")
    page.locator("#sensitivity-points").fill("3")
    _calculate(page)

    expect(page.locator("#sensitivity-section")).to_be_visible()
    expect(page.locator("#sensitivity-table tbody tr")).to_have_count(3)
    expect(page.locator("#sensitivity-table tbody")).to_contain_text("no finite joint solution")

    with page.expect_download() as scenario_info:
        page.locator("#export-scenario-csv").click()
    scenario = scenario_info.value
    scenario_path = tmp_path / scenario.suggested_filename
    scenario.save_as(scenario_path)
    scenario_text = scenario_path.read_text(encoding="utf-8")
    assert scenario.suggested_filename.endswith("-scenario-targets.csv")
    assert "required_information_multiplier" in scenario_text
    assert "Joint mandatory requirement" in scenario_text
    assert len(scenario_text.splitlines()) == 5

    with page.expect_download() as sensitivity_info:
        page.locator("#export-sensitivity-csv").click()
    sensitivity = sensitivity_info.value
    sensitivity_path = tmp_path / sensitivity.suggested_filename
    sensitivity.save_as(sensitivity_path)
    sensitivity_text = sensitivity_path.read_text(encoding="utf-8")
    assert sensitivity.suggested_filename.endswith("-sensitivity.csv")
    assert "sensitivity_joint" in sensitivity_text
    assert len(sensitivity_text.splitlines()) == 13

    for selector, suffix in [
        ("#export-figure", "-figure.png"),
        ("#export-dashboard", "-summary.png"),
    ]:
        with page.expect_download(timeout=30_000) as png_info:
            page.locator(selector).click()
        download = png_info.value
        png_path = tmp_path / download.suggested_filename
        download.save_as(png_path)
        assert download.suggested_filename.endswith(suffix)
        assert png_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

    page.locator("#copy-reviewer").click()
    expect(page.locator("#runtime-status")).to_have_text("Reviewer text copied.")
    assert "formal study-design analysis" in page.evaluate("navigator.clipboard.readText()")
    page.locator("#copy-caption").click()
    expect(page.locator("#runtime-status")).to_have_text("Figure caption copied.")
    assert "sensitivity analysis" in page.evaluate("navigator.clipboard.readText()")


def test_sample_size_projection_requires_active_opt_in(
    page: Page,
    app_url: str,
) -> None:
    _ready(page, app_url)
    expect(page.locator("#current-effective-n")).to_be_disabled()
    page.get_by_text("Optional approximate sample-size projection", exact=True).click()
    page.locator("#sample-size-projection-enabled").check()
    expect(page.locator("#current-effective-n")).to_be_enabled()
    page.locator("#current-effective-n").fill("100")
    _calculate(page)

    expect(page.locator("#sample-size-section")).to_be_visible()
    expect(page.locator("#sample-size-result")).to_contain_text("Approximate required n: 491")
    expect(page.locator("#sample-size-result")).to_contain_text(
        "not a design-specific sample-size calculation"
    )


def test_mobile_keyboard_privacy_and_reset_smoke(page: Page, app_url: str) -> None:
    requests: list[tuple[str, str | None]] = []
    page.context.on(
        "request",
        lambda request: requests.append((request.url, request.post_data)),
    )
    page.set_viewport_size({"width": 390, "height": 844})
    _ready(page, app_url)
    initial_url = page.url
    page.locator("#target-true-effect").fill("0.234567891")
    page.locator("#effect-type").focus()
    page.keyboard.press("Tab")
    expect(page.locator("input[name='precision_mode']").first).to_be_focused()
    _calculate(page)

    assert page.url == initial_url
    assert page.evaluate("localStorage.length") == 0
    assert page.evaluate("sessionStorage.length") == 0
    assert page.evaluate("document.cookie") == ""
    assert page.evaluate("document.documentElement.scrollWidth") == page.evaluate(
        "document.documentElement.clientWidth"
    )
    serialized_requests = "\n".join(f"{url}\n{body or ''}" for url, body in requests)
    assert "0.234567891" not in serialized_requests
    expect(page.locator(".controls")).to_be_visible()
    expect(page.locator(".results")).to_be_visible()

    page.locator("button[type='reset']").click()
    expect(page.locator("#result")).to_be_hidden()
    expect(page.locator("#export-scenario-csv")).to_be_disabled()
