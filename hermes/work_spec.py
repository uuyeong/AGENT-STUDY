"""Read and validate one sanitized team-work request."""

from dataclasses import dataclass
from pathlib import Path
import re
import tomllib


SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
ROLES = ("pm", "product", "marketing", "client", "producer")
FORMATS = ("md", "csv")
EVIDENCE_STATES = ("fact", "decision", "proposal", "open")


class JobError(ValueError):
    """A request or execution result cannot be used."""


@dataclass(frozen=True)
class Track:
    id: str
    label: str
    objective: str


@dataclass(frozen=True)
class Output:
    id: str
    track: str
    audience: str
    goal: str
    checks: tuple[str, ...]
    needs: tuple[str, ...]
    format: str
    columns: tuple[str, ...]


@dataclass(frozen=True)
class Evidence:
    id: str
    status: str
    source: str
    summary: str


@dataclass(frozen=True)
class Job:
    root: Path
    title: str
    brief: str
    tracks: dict[str, Track]
    outputs: dict[str, Output]
    evidence: dict[str, Evidence]


def text(value, where):
    if not isinstance(value, str) or not value.strip():
        raise JobError(f"{where}에 비어 있지 않은 문자열을 넣으세요.")
    return value.strip()


def texts(value, where):
    if not isinstance(value, list):
        raise JobError(f"{where}에 문자열 배열을 넣으세요.")
    return tuple(text(item, where) for item in value)


def slug(value, where):
    if not isinstance(value, str) or not SLUG.fullmatch(value) or len(value) > 64:
        raise JobError(f"{where}에는 64자 이하의 소문자 영숫자와 하이픈을 사용하세요.")
    return value


def table_rows(data, key):
    rows = data.get(key)
    if not isinstance(rows, list) or not rows or any(not isinstance(row, dict) for row in rows):
        raise JobError(f"[[{key}]] 항목이 필요합니다.")
    indexed = {}
    for row in rows:
        row_id = slug(row.get("id"), f"{key}.id")
        if row_id in indexed:
            raise JobError(f"{key}의 ID가 중복됐습니다. {row_id}")
        indexed[row_id] = row
    return indexed


def request_file(root, name):
    path = root / name
    if path.is_symlink() or not path.is_file():
        raise JobError(f"의뢰 폴더에 일반 파일 {name}이 필요합니다.")
    return path


def topological_outputs(outputs):
    remaining = dict(outputs)
    ordered = {}
    while remaining:
        ready = [key for key, output in remaining.items() if set(output.needs) <= ordered.keys()]
        if not ready:
            raise JobError("산출물 선행 관계에 순환이 있습니다.")
        for key in ready:
            ordered[key] = remaining.pop(key)
    return ordered


def load_job(root):
    root = Path(root).resolve()
    try:
        brief = text(request_file(root, "brief.md").read_text(encoding="utf-8"), "brief.md")
        spec = tomllib.loads(request_file(root, "job.toml").read_text(encoding="utf-8"))
        evidence_spec = tomllib.loads(request_file(root, "evidence.toml").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise JobError(f"의뢰 파일을 읽을 수 없습니다. {error}") from error

    tracks = {
        key: Track(key, text(row.get("label"), f"{key}.label"), text(row.get("objective"), f"{key}.objective"))
        for key, row in table_rows(spec, "tracks").items()
    }
    outputs = {}
    for key, row in table_rows(spec, "outputs").items():
        track = slug(row.get("track"), f"{key}.track")
        if track not in tracks or key == "readme":
            raise JobError(f"{key}의 트랙 또는 산출물 ID가 유효하지 않습니다.")
        output_format = row.get("format")
        columns = texts(row.get("columns", []), f"{key}.columns")
        if output_format is not None and output_format not in FORMATS:
            raise JobError(f"{key}의 형식은 md 또는 csv여야 합니다.")
        if len(set(columns)) != len(columns) or any(len(column.splitlines()) != 1 for column in columns):
            raise JobError(f"{key}의 Markdown 항목 필드가 유효하지 않습니다.")
        checks = texts(row.get("checks"), f"{key}.checks")
        if not checks:
            raise JobError(f"{key}에 검수 기준이 필요합니다.")
        outputs[key] = Output(
            key, track, text(row.get("audience"), f"{key}.audience"), text(row.get("goal"), f"{key}.goal"),
            checks, texts(row.get("needs", []), f"{key}.needs"), "md", columns,
        )
    if {output.track for output in outputs.values()} != tracks.keys():
        raise JobError("각 트랙에 최소 한 개의 산출물이 필요합니다.")
    for output in outputs.values():
        for need in output.needs:
            if need not in outputs or outputs[need].track != output.track:
                raise JobError(f"{output.id}의 선행 산출물은 같은 트랙에 있어야 합니다. {need}")

    evidence = {}
    for key, row in table_rows(evidence_spec, "evidence").items():
        status = text(row.get("status"), f"{key}.status")
        if status not in EVIDENCE_STATES:
            raise JobError(f"{key}.status를 확인하세요. {', '.join(EVIDENCE_STATES)}")
        evidence[key] = Evidence(
            key, status, text(row.get("source"), f"{key}.source"), text(row.get("summary"), f"{key}.summary"),
        )
    return Job(root, text(spec.get("title"), "title"), brief, tracks, topological_outputs(outputs), evidence)
