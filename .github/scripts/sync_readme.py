"""
HANDOFF.md frontmatter -> README.md AUTO:STATUS 영역 자동 동기화.

사용:
    python .github/scripts/sync_readme.py [--check]

- 기본: README.md를 갱신 (변경 시 exit 0, 변경 없으면 exit 0)
- --check: 변경 필요 여부만 확인 (변경 필요 시 exit 1, 동기화 상태면 exit 0)

GitHub Actions에서:
    1. sync_readme.py 실행
    2. git diff 확인 -> 변경 있으면 자동 commit + push
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HANDOFF_PATH = REPO_ROOT / "HANDOFF.md"
README_PATH = REPO_ROOT / "README.md"

STATUS_START = "<!-- AUTO:STATUS:START -->"
STATUS_END = "<!-- AUTO:STATUS:END -->"
VALIDATION_START = "<!-- AUTO:VALIDATION:START -->"
VALIDATION_END = "<!-- AUTO:VALIDATION:END -->"

REMOTE_BASE_URL = "https://github.com/cho1124/Aria"

LAYER_LABELS = {
    "L1": "L1 Web Verify",
    "L2": "L2 Code Review",
    "L3": "L3 Adversarial Triad",
    "L4": "L4 Build Gate",
}


def parse_frontmatter(text: str) -> dict[str, str]:
    """YAML frontmatter (--- ... ---)에서 단순 key: value 추출.

    PyYAML 미사용 (의존성 최소화). 주석/단순 string/number만 지원.
    """
    if not text.startswith("---"):
        return {}

    end = text.find("\n---", 3)
    if end == -1:
        return {}

    block = text[3:end].strip()
    result: dict[str, str] = {}
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        result[key] = value
    return result


def render_status_block(meta: dict[str, str]) -> str:
    """frontmatter dict -> README의 STATUS 마커 사이에 들어갈 markdown."""

    def emoji(value: str) -> str:
        v = value.lower()
        if v in ("passed", "completed", "ok", "success"):
            return "✅"
        if v in ("pending", "in_progress", "running"):
            return "⏳"
        if v in ("failed", "error", "broken"):
            return "❌"
        return ""

    commit = meta.get("last_commit", "—")
    commit_md = f"[`{commit}`]({REMOTE_BASE_URL}/commit/{commit})" if commit != "—" else "—"

    session = meta.get("session", "—")
    session_total = meta.get("session_total", "")
    session_label = f"Session {session}" + (f" / {session_total}" if session_total else "")

    rows = [
        ("현재 세션", session_label),
        ("세션 포커스", meta.get("session_focus", "—")),
        ("세션 상태", f"{emoji(meta.get('session_status', ''))} {meta.get('session_status', '—')}".strip()),
        ("현재 마일스톤", meta.get("current_milestone", "—")),
        ("다음 마일스톤", meta.get("next_milestone", "—")),
        ("마지막 세션 날짜", meta.get("last_session_date", "—")),
        ("마지막 commit", commit_md),
        ("빌드 (로컬)", f"{emoji(meta.get('build_status', ''))} {meta.get('build_status', '—')}".strip()),
        ("CI", f"{emoji(meta.get('ci_status', ''))} {meta.get('ci_status', '—')}".strip()),
        ("청취 검증", f"{emoji(meta.get('audio_verification', ''))} {meta.get('audio_verification', '—')}".strip()),
        ("다음 액션", meta.get("next_action", "—")),
        ("최근 발견", meta.get("recent_finding", "—")),
    ]

    lines: list[str] = []
    lines.append(STATUS_START)
    lines.append("*아래 표는 [HANDOFF.md](HANDOFF.md) frontmatter에서 자동 동기화됩니다 (push 시 GitHub Actions).*")
    lines.append("")
    lines.append("| 항목 | 값 |")
    lines.append("|------|------|")
    for label, value in rows:
        lines.append(f"| {label} | {value} |")
    lines.append(STATUS_END)
    return "\n".join(lines)


def replace_status_block(readme: str, new_block: str) -> str:
    return _replace_block(readme, STATUS_START, STATUS_END, new_block)


def render_validation_block(meta: dict[str, str]) -> str:
    """Layer별 검증 실적 표 렌더링."""

    def emoji_for(value: str) -> str:
        v = value.lower()
        if v == "passed":
            return "✅"
        if v == "failed":
            return "❌"
        if v == "skipped":
            return "⏭️"
        if v == "not_run":
            return "⬜"
        return ""

    lines: list[str] = []
    lines.append(VALIDATION_START)
    lines.append("*아래 표는 [HANDOFF.md](HANDOFF.md) frontmatter의 layer_*_status / layer_*_note 에서 자동 동기화됩니다.*")
    lines.append("")
    lines.append("| Layer | 상태 | 비고 |")
    lines.append("|---|---|---|")
    for layer_id, label in LAYER_LABELS.items():
        status = meta.get(f"layer_{layer_id}_status", "not_run")
        note = meta.get(f"layer_{layer_id}_note", "—")
        cell = f"{emoji_for(status)} {status}".strip()
        lines.append(f"| {label} | {cell} | {note} |")
    lines.append(VALIDATION_END)
    return "\n".join(lines)


def replace_validation_block(readme: str, new_block: str) -> str:
    return _replace_block(readme, VALIDATION_START, VALIDATION_END, new_block)


def _replace_block(text: str, start_marker: str, end_marker: str, new_block: str) -> str:
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker),
        flags=re.DOTALL,
    )
    if not pattern.search(text):
        raise SystemExit(
            f"README.md에 {start_marker} ~ {end_marker} 마커가 없습니다. "
            "마커 영역을 먼저 만들어주세요."
        )
    return pattern.sub(new_block, text)


def main() -> int:
    check_only = "--check" in sys.argv[1:]

    handoff_text = HANDOFF_PATH.read_text(encoding="utf-8")
    meta = parse_frontmatter(handoff_text)
    if not meta:
        print("ERROR: HANDOFF.md에 YAML frontmatter가 없거나 빈 값입니다.", file=sys.stderr)
        return 2

    readme_text = README_PATH.read_text(encoding="utf-8")
    updated = readme_text
    updated = replace_status_block(updated, render_status_block(meta))
    updated = replace_validation_block(updated, render_validation_block(meta))

    if updated == readme_text:
        print("README.md는 이미 동기화 상태입니다.")
        return 0

    if check_only:
        print("README.md 갱신 필요 (현재 out-of-sync).")
        return 1

    README_PATH.write_text(updated, encoding="utf-8")
    print("README.md 갱신 완료.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
