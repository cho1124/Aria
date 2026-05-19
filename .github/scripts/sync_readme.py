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

REMOTE_BASE_URL = "https://github.com/cho1124/Aria"


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

    rows = [
        ("현재 세션", f"Session {meta.get('session', '—')}"),
        ("세션 포커스", meta.get("session_focus", "—")),
        ("세션 상태", f"{emoji(meta.get('session_status', ''))} {meta.get('session_status', '—')}".strip()),
        ("마지막 세션 날짜", meta.get("last_session_date", "—")),
        ("마지막 commit", commit_md),
        ("빌드 (로컬)", f"{emoji(meta.get('build_status', ''))} {meta.get('build_status', '—')}".strip()),
        ("CI", f"{emoji(meta.get('ci_status', ''))} {meta.get('ci_status', '—')}".strip()),
        ("청취 검증", f"{emoji(meta.get('audio_verification', ''))} {meta.get('audio_verification', '—')}".strip()),
        ("다음 액션", meta.get("next_action", "—")),
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
    pattern = re.compile(
        re.escape(STATUS_START) + r".*?" + re.escape(STATUS_END),
        flags=re.DOTALL,
    )
    if not pattern.search(readme):
        raise SystemExit(
            "README.md에 AUTO:STATUS 마커가 없습니다. "
            f"`{STATUS_START}` 와 `{STATUS_END}` 사이를 만들어주세요."
        )
    return pattern.sub(new_block, readme)


def main() -> int:
    check_only = "--check" in sys.argv[1:]

    handoff_text = HANDOFF_PATH.read_text(encoding="utf-8")
    meta = parse_frontmatter(handoff_text)
    if not meta:
        print("ERROR: HANDOFF.md에 YAML frontmatter가 없거나 빈 값입니다.", file=sys.stderr)
        return 2

    new_block = render_status_block(meta)
    readme_text = README_PATH.read_text(encoding="utf-8")
    updated = replace_status_block(readme_text, new_block)

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
