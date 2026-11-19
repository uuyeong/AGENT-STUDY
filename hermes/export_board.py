"""Hermes 칸반 보드(odoc)의 카드, 연결, 완료 요약, 팀원 간 handoffs를 Markdown으로 내보낸다.

칸반 기록은 Hermes DB(~/.hermes/kanban/boards/odoc/kanban.db)에만 있어서,
제출용 증거로 hermes/workspace/results/00_board.md 에 남긴다.

사용법 (프로젝트 루트에서):  python3 hermes/export_board.py
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

BOARD = "odoc"
OUT = Path(__file__).resolve().parent / "workspace" / "results" / "00_board.md"


def kanban(*args: str):
    out = subprocess.run(["hermes", "kanban", "--board", BOARD, *args, "--json"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def ts(value) -> str:
    return datetime.fromtimestamp(int(value)).strftime("%H:%M:%S") if value else "-"


def cell(text) -> str:
    return str(text or "").replace("|", "/").replace("\n", " ")


def main() -> None:
    listed = kanban("list", "--sort", "created")
    tasks = listed if isinstance(listed, list) else listed.get("tasks", [])
    details = [kanban("show", t["id"]) for t in tasks]

    lines = [f"# Hermes 칸반 보드 기록: `{BOARD}`", "",
             f"> 내보낸 시각: {datetime.now():%Y-%m-%d %H:%M} · `python3 hermes/export_board.py`", "",
             "## 카드", "",
             "| 카드 | 담당 | 만든 사람 | 부모 | 상태 | 시작 | 완료 | 제목 |", "|---|---|---|---|---|---|---|---|"]
    for d in details:
        t = d["task"]
        creator = "오너" if t.get("created_by") == "user" else t.get("created_by")
        lines.append(f"| {t['id']} | {t['assignee']} | {creator} | {', '.join(d['parents']) or '-'} | "
                     f"{t['status']} | {ts(t.get('started_at'))} | {ts(t.get('completed_at'))} | {cell(t['title'])} |")

    lines += ["", "## 완료 요약", ""]
    handoffs = []
    for d in details:
        t, run = d["task"], (d["runs"] or [{}])[-1]
        lines += [f"### {t['id']} · {t['assignee']} · {t['title']}", "", run.get("summary") or "-", ""]
        meta = run.get("metadata") or {}
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except ValueError:
                meta = {}
        for h in meta.get("handoffs") or []:
            handoffs.append((t["id"], t["assignee"], h.get("to", "?"), h.get("message", "")))

    lines += ["## 팀원 간 handoffs (`kanban_complete`의 metadata)", "",
              "| 카드 | 보낸 사람 | 받는 사람 | 내용 |", "|---|---|---|---|"]
    lines += [f"| {c} | {s} | {to} | {cell(m)} |" for c, s, to, m in handoffs] or ["| - | - | - | 없음 |"]

    created = [d["task"] for d in details if d["task"].get("created_by") not in (None, "user")]
    lines += ["", f"오너가 만든 카드 {len(details) - len(created)}장, "
                  f"에이전트(PM)가 `kanban_create`로 만든 카드 {len(created)}장, handoffs {len(handoffs)}건.", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"→ {OUT}")


if __name__ == "__main__":
    main()
