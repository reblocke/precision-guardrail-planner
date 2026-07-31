from __future__ import annotations

import re
import subprocess
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_ROOT = PROJECT_ROOT / ".github" / "workflows"
GH_CLI_VERSION = "2.93.0"
GH_CLI_LINUX_AMD64_SHA256 = "02d1290eba130e0b896f3709ffff22e1c75a51475ddb70476a85abc6b5807af0"


def test_makefile_exposes_required_commands() -> None:
    makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")

    for target in [
        "stage-web:",
        "fmt:",
        "fmt-check:",
        "lint:",
        "test:",
        "e2e:",
        "verify:",
        "serve:",
        "clean:",
    ]:
        assert target in makefile


def test_ci_and_pages_use_repository_targets() -> None:
    ci = (PROJECT_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    pages = (PROJECT_ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")

    assert "make fmt-check" in ci
    assert "make lint" in ci
    assert "make test" in ci
    assert "make e2e" in ci
    assert "make e2e-webkit-smoke" in ci
    assert "make stage-web" in pages
    assert "enablement: true" in pages
    assert "web" in pages


def test_workflows_pin_external_actions_to_full_shas_with_version_comments() -> None:
    use_value_pattern = re.compile(r"^\s*(?:-\s+)?uses:\s+(?P<value>\S+)(?:\s+#.*)?$")
    external_use_pattern = re.compile(
        r"^\s*(?:-\s+)?uses:\s+"
        r"(?P<action>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_./-]+)?)"
        r"@(?P<sha>[0-9a-f]{40})"
        r"\s+#\s+v(?P<version>\d+\.\d+\.\d+)\s*$"
    )
    violations: list[str] = []
    external_uses_count = 0
    workflows = sorted({*WORKFLOW_ROOT.glob("*.yml"), *WORKFLOW_ROOT.glob("*.yaml")})

    for workflow in workflows:
        for line_number, line in enumerate(
            workflow.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if "uses:" not in line:
                continue
            parsed_use = use_value_pattern.fullmatch(line)
            if parsed_use is None:
                violations.append(f"{workflow.name}:{line_number}:{line.strip()}")
                continue
            if parsed_use.group("value").startswith("./"):
                continue
            external_uses_count += 1
            if external_use_pattern.fullmatch(line) is None:
                violations.append(f"{workflow.name}:{line_number}:{line.strip()}")

    assert external_uses_count > 0
    assert violations == []


def test_workflow_permissions_credentials_and_release_cache_are_fail_closed() -> None:
    ci = (WORKFLOW_ROOT / "ci.yml").read_text(encoding="utf-8")
    pages = (WORKFLOW_ROOT / "pages.yml").read_text(encoding="utf-8")
    release = (WORKFLOW_ROOT / "release.yml").read_text(encoding="utf-8")

    assert "permissions:\n  contents: read" in ci
    assert "permissions: {}" in pages
    assert "build:\n    name: Build Pages artifact\n    permissions:\n      contents: read" in pages
    assert (
        "deploy:\n    name: Deploy Pages\n    needs: build\n    permissions:\n"
        "      pages: write # Publish the verified Pages artifact.\n"
        "      id-token: write # Authenticate the Pages deployment." in pages
    )
    pages_build, pages_deploy = pages.split("\n  deploy:", maxsplit=1)
    assert "pages: write" not in pages_build
    assert "id-token: write" not in pages_build
    assert "actions/configure-pages@" not in pages_build
    assert "contents: read" not in pages_deploy
    assert "actions/configure-pages@" in pages_deploy

    assert "permissions: {}" in release
    assert (
        "verify-and-build:\n    name: Verify tag and build release bundle\n"
        "    permissions:\n      contents: read" in release
    )
    verify_build, publish = release.split("\n  publish:", maxsplit=1)
    assert "enable-cache: true" not in verify_build
    assert "enable-cache: false" in verify_build
    assert release.count("contents: write") == 1
    assert (
        "publish:\n    name: Verify and publish immutable release\n"
        "    needs: verify-and-build\n    permissions:\n"
        "      contents: write # Create and publish the verified GitHub release." in release
    )
    assert "attestations: read # Required to verify the immutable release" in publish
    assert "attestations: read" not in verify_build
    assert "contents: read" not in publish

    workflow_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted({*WORKFLOW_ROOT.glob("*.yml"), *WORKFLOW_ROOT.glob("*.yaml")})
    )
    checkout_count = workflow_text.count("uses: actions/checkout@")
    assert checkout_count > 0
    assert workflow_text.count("persist-credentials: false") == checkout_count


def test_release_note_guards_reject_whitespace_before_transfer_and_publish(
    tmp_path: Path,
) -> None:
    release = (WORKFLOW_ROOT / "release.yml").read_text(encoding="utf-8")
    verify_build, publish = release.split("\n  publish:", maxsplit=1)

    assert "grep -q '[^[:space:]]' \"$bundle/release-notes.md\"" in verify_build
    assert "grep -q '[^[:space:]]' dist/release-notes.md" in publish
    assert release.count("grep -q '[^[:space:]]'") == 2
    assert 'test -s "$bundle/release-notes.md"' not in release
    assert "test -s dist/release-notes.md" not in release

    notes = tmp_path / "release-notes.md"
    for whitespace_only in ("", "\n", " \t\r\n"):
        notes.write_text(whitespace_only, encoding="utf-8")
        result = subprocess.run(
            ["grep", "-q", "[^[:space:]]", str(notes)],
            check=False,
        )
        assert result.returncode == 1

    notes.write_text("\nRelease notes\n", encoding="utf-8")
    result = subprocess.run(
        ["grep", "-q", "[^[:space:]]", str(notes)],
        check=False,
    )
    assert result.returncode == 0


def test_release_is_annotated_tag_main_contained_draft_first_and_immutable() -> None:
    release = (WORKFLOW_ROOT / "release.yml").read_text(encoding="utf-8")

    version_parse = (
        "python -I -c 'import tomllib; "
        'print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])\''
    )
    assert version_parse in release
    assert 'test "$GITHUB_REF_NAME" = "v${project_version}"' in release
    assert 'git cat-file -t "$GITHUB_REF_NAME"' in release
    assert "/git/ref/tags/${GITHUB_REF_NAME}" in release
    assert 'git rev-parse "refs/tags/$GITHUB_REF_NAME"' in release
    assert "--jq '.tag'" in release
    assert ".verification.verified" not in release
    assert ".verification.reason" not in release
    assert "--jq '.object.sha'" in release
    assert "--jq '.object.type'" in release
    assert ')" = "commit"' in release
    assert '"https://github.com/${GITHUB_REPOSITORY}.git"' in release
    assert "+refs/heads/main:refs/remotes/origin/main" in release
    assert 'git merge-base --is-ancestor "$GITHUB_SHA" refs/remotes/origin/main' in release
    assert release.index("/git/ref/tags/${GITHUB_REF_NAME}") < release.index("git fetch")
    assert release.index("git merge-base --is-ancestor") < release.index(version_parse)
    assert release.index("/git/ref/tags/${GITHUB_REF_NAME}") < release.index("uv sync --locked")

    assert "/immutable-releases" not in release
    assert "RELEASE_SETTINGS_READ_TOKEN" not in release
    assert "sha256sum --check SHA256SUMS" in release
    assert "actions/upload-artifact@" in release
    assert "actions/download-artifact@" in release
    assert "--draft" in release
    assert "--verify-tag" in release
    assert "--prerelease" not in release
    assert 'awk -v version="$version"' in release
    assert "--notes-file dist/release-notes.md" in release
    assert "--notes-file CHANGELOG.md" not in release
    assert "jq --exit-status --join-output '.body'" in release
    assert "cmp --silent dist/release-notes.md" in release
    assert "GH_REPO: ${{ github.repository }}" in release
    assert "gh release download" in release
    assert "diff --recursive --brief dist/assets remote-dist" in release
    assert "--draft=false" in release
    assert "--json isImmutable" in release
    assert "gh release verify" in release
    assert "gh release verify-asset" in release
    publish = release[release.index("\n  publish:") :]
    assert publish.count("GH_TOKEN: ${{ github.token }}") == 3
    assert (
        release.index("gh release create")
        < release.index("gh release download")
        < release.index("--draft=false")
    )


def test_release_installs_checksummed_github_cli_before_credentialed_commands() -> None:
    release = (WORKFLOW_ROOT / "release.yml").read_text(encoding="utf-8")

    assert f'GH_CLI_VERSION: "{GH_CLI_VERSION}"' in release
    assert f'GH_CLI_LINUX_AMD64_SHA256: "{GH_CLI_LINUX_AMD64_SHA256}"' in release
    assert release.count("Install checksummed GitHub CLI") == 2
    assert release.count("sha256sum --check --strict -") == 2
    assert release.count("Confirm the checksummed GitHub CLI is selected") == 2
    assert release.index("Install checksummed GitHub CLI") < release.index(
        "Verify the annotated remote tag and event commit"
    )
    publish = release[release.index("\n  publish:") :]
    assert publish.index("Confirm the checksummed GitHub CLI is selected") < publish.index(
        "gh release create"
    )


def test_dependabot_covers_locked_python_and_actions_without_auto_merge() -> None:
    dependabot = (PROJECT_ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")

    assert 'package-ecosystem: "uv"' in dependabot
    assert 'package-ecosystem: "github-actions"' in dependabot
    assert dependabot.count('interval: "weekly"') == 2
    assert dependabot.count("default-days: 7") == 2
    assert "python-dependencies:" in dependabot
    assert "github-actions:" in dependabot
    assert "automerge" not in dependabot.lower()


def test_public_coordination_files_preserve_scope_and_private_reporting() -> None:
    security = (PROJECT_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    normalized_security = " ".join(security.lower().split())
    contributing = (PROJECT_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    issue_config = (PROJECT_ROOT / ".github/ISSUE_TEMPLATE/config.yml").read_text(encoding="utf-8")
    engineering_issue = (PROJECT_ROOT / ".github/ISSUE_TEMPLATE/engineering-bug.yml").read_text(
        encoding="utf-8"
    )
    scientific_issue = (
        PROJECT_ROOT / ".github/ISSUE_TEMPLATE/scientific-discrepancy.yml"
    ).read_text(encoding="utf-8")
    accessibility_issue = (
        PROJECT_ROOT / ".github/ISSUE_TEMPLATE/accessibility-report.yml"
    ).read_text(encoding="utf-8")
    security_contact = (PROJECT_ROOT / ".github/ISSUE_TEMPLATE/security-contact.yml").read_text(
        encoding="utf-8"
    )
    pull_request = (PROJECT_ROOT / ".github/PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")

    assert "/security/advisories/new" in security
    assert "Do not disclose vulnerability details in a public issue" in security
    assert "protected health information" in security.lower()
    assert "synthetic" in security.lower()
    assert "does not establish clinical decision support" in normalized_security
    assert "wald formula" in contributing.lower()
    assert "private" in contributing.lower()
    assert "release_settings_read_token" not in contributing.lower()
    assert "blank_issues_enabled: false" in issue_config
    assert "/security/advisories/new" in issue_config
    assert "protected health information" in engineering_issue.lower()
    assert "behavior owned by this repository" in engineering_issue.lower()
    assert "authoritative upstream" in engineering_issue.lower()
    assert "wald-inference-core" in scientific_issue
    assert "clinical advice" in scientific_issue.lower()
    assert "assistive technology" in accessibility_issue.lower()
    assert "protected health information" in accessibility_issue.lower()
    assert "include no vulnerability details" in security_contact.lower()
    assert "protected health information" in security_contact.lower()
    assert "make verify" in pull_request
    assert "copies no Wald formula" in pull_request
    assert "inverse precision" in contributing.lower()
    assert "information as automatically" in contributing.lower()
    assert "design-specific sample-size" in pull_request.lower()


def test_current_release_docs_match_credential_free_annotated_tag_policy() -> None:
    current_docs = (
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "CHANGELOG.md",
        PROJECT_ROOT / "CONTRIBUTING.md",
        PROJECT_ROOT / "docs" / "MAINTENANCE.md",
        PROJECT_ROOT / "docs" / "VALIDATION.md",
    )
    for path in current_docs:
        text = path.read_text(encoding="utf-8")
        assert "RELEASE_SETTINGS_READ_TOKEN" not in text
        assert re.search(r"\bsigned\b", text, flags=re.IGNORECASE) is None

    decisions = (PROJECT_ROOT / "docs" / "DECISIONS.md").read_text(encoding="utf-8")
    assert "2026-07-31 — Release automation uses only the job-scoped GitHub token" in decisions
    assert "supersedes only the 2026-07-30 requirements" in decisions
    assert "GitHub-verified signed annotated tag" in decisions


def test_generated_stage_is_ignored_and_not_tracked() -> None:
    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "web/assets/py/" in gitignore
    assert (
        subprocess.run(
            ["git", "check-ignore", "web/assets/py/manifest.json"],
            cwd=PROJECT_ROOT,
            check=False,
        ).returncode
        == 0
    )
    assert (
        subprocess.run(
            ["git", "ls-files", "web/assets/py"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        == ""
    )


def test_required_public_documentation_is_complete_and_has_no_author_prompts() -> None:
    required = [
        "README.md",
        "LICENSE",
        "CITATION.cff",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "AGENTS.md",
        "CHANGELOG.md",
        "llms.txt",
        "docs/SCIENTIFIC_SCOPE.md",
        "docs/VALIDATION.md",
        "docs/PRIVACY.md",
        "docs/DECISIONS.md",
        "docs/MAINTENANCE.md",
        "docs/RUNTIME_DEPENDENCIES.md",
    ]
    contents = []
    for relative in required:
        path = PROJECT_ROOT / relative
        assert path.is_file(), relative
        contents.append(path.read_text(encoding="utf-8"))
    assert "AUTHOR ACTION REQUIRED" not in "\n".join(contents)


def test_license_identity_is_canonical() -> None:
    license_text = (PROJECT_ROOT / "LICENSE").read_text(encoding="utf-8")
    citation = (PROJECT_ROOT / "CITATION.cff").read_text(encoding="utf-8")

    assert "Copyright (c) 2026 Brian Locke" in license_text
    assert "MIT License" in license_text
    assert "family-names: Locke" in citation
    assert "given-names: Brian" in citation
    assert "license: MIT" in citation


def test_readme_related_tools_has_catalog_core_marker() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    related = readme.split("## Related Wald tools", maxsplit=1)[1].split(
        "\n## ",
        maxsplit=1,
    )[0]

    assert "wald-inference Core v0.4.2" in related
    assert "https://github.com/reblocke/wald-inference-core/releases/tag/v0.4.2" in related


def test_readme_records_current_release_and_software_citation() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    citation = (PROJECT_ROOT / "CITATION.cff").read_text(encoding="utf-8")
    maintenance = (PROJECT_ROOT / "docs" / "MAINTENANCE.md").read_text(encoding="utf-8")
    project = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    version = project["version"]

    assert f"Current app version: `{version}`." in readme
    assert (
        f"https://github.com/reblocke/precision-guardrail-planner/releases/tag/v{version}" in readme
    )
    assert "Release maturity: experimental software." in readme
    assert "GitHub publication state is recorded on the versioned release page:" in readme
    assert "Cite the exact tagged software release or commit used" in readme
    assert "[CITATION.cff](CITATION.cff)" in readme
    assert f"version: {version}" in citation
    assert "Status: experimental, actively maintained software." in maintenance
    assert "actively maintained prerelease software" not in maintenance
