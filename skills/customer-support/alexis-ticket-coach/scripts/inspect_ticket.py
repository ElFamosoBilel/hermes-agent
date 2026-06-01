#!/usr/bin/env python3
"""Build a compact Alexis ticket evidence bundle for Hermes Ticket Coach."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


DEFAULT_DATA_DIR = "/opt/alexis-bot/data-prod"


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default
    except Exception as exc:
        return {"_read_error": str(exc)}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                obj = {"_raw": line}
            if isinstance(obj, dict):
                rows.append(obj)
    except FileNotFoundError:
        pass
    return rows


def norm_id(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("#"):
        text = text[1:]
    if text.startswith("ticket-"):
        text = text[7:]
    digits = "".join(ch for ch in text if ch.isdigit())
    if digits:
        return str(int(digits))
    return text


def id_matches(value: Any, wanted: str) -> bool:
    return norm_id(value) == wanted


def nested_id_match(obj: Any, wanted: str) -> bool:
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_l = str(key).lower()
            if key_l in {"ticketid", "ticket_id", "ticket", "id", "ticketnumber", "ticket_number"}:
                if id_matches(value, wanted):
                    return True
            if nested_id_match(value, wanted):
                return True
    elif isinstance(obj, list):
        return any(nested_id_match(item, wanted) for item in obj)
    return False


def find_ticket(tickets_data: Any, wanted: str) -> Any:
    if isinstance(tickets_data, dict):
        items = tickets_data.get("items")
        if isinstance(items, dict):
            iterable = items.values()
        elif isinstance(items, list):
            iterable = items
        else:
            iterable = tickets_data.values()
    elif isinstance(tickets_data, list):
        iterable = tickets_data
    else:
        iterable = []

    for item in iterable:
        if isinstance(item, dict) and (
            id_matches(item.get("id"), wanted)
            or id_matches(item.get("ticketId"), wanted)
            or id_matches(item.get("number"), wanted)
        ):
            return item
    return None


def find_transcript(data_dir: Path, raw_ticket_id: str, wanted: str) -> tuple[str | None, str | None]:
    raw = raw_ticket_id.strip().lstrip("#")
    names = [
        f"transcript-{wanted}.txt",
        f"transcript-{raw}.txt",
        f"{wanted}.txt",
        f"{raw}.txt",
        f"ticket-{wanted}.txt",
        f"ticket-{raw}.txt",
        f"#{raw}.txt",
    ]
    dirs = [data_dir, data_dir / "transcripts", data_dir / "transcript"]
    for directory in dirs:
        for name in names:
            path = directory / name
            if path.exists():
                return str(path), path.read_text(encoding="utf-8", errors="replace")
    return None, None


def filter_rows(rows: list[dict[str, Any]], wanted: str, limit: int) -> list[dict[str, Any]]:
    matched = [row for row in rows if nested_id_match(row, wanted)]
    return matched[-limit:]


def dict_lookup_by_ticket(obj: Any, wanted: str) -> Any:
    if not isinstance(obj, dict):
        return None
    for key, value in obj.items():
        if id_matches(key, wanted):
            return value
    for value in obj.values():
        if isinstance(value, dict) and nested_id_match(value, wanted):
            return value
    return None


def build_bundle(data_dir: Path, ticket_id: str, limit: int) -> dict[str, Any]:
    wanted = norm_id(ticket_id)
    missing: list[str] = []

    tickets_path = data_dir / "tickets.json"
    tickets_data = read_json(tickets_path, {})
    ticket = find_ticket(tickets_data, wanted)
    if ticket is None:
        if tickets_path.exists():
            missing.append(f"ticket {ticket_id} not found in {tickets_path}")
        else:
            missing.append(str(tickets_path))

    transcript_path, transcript = find_transcript(data_dir, ticket_id, wanted)
    if transcript is None:
        missing.append(f"{data_dir}/transcripts or transcript-<ticket>.txt")

    usage_rows = read_jsonl(data_dir / "ai-usage.jsonl")
    feedback_rows = read_jsonl(data_dir / "ai-feedback.jsonl")
    memory_rows = read_jsonl(data_dir / "ai-memory.jsonl")
    actions_data = read_json(data_dir / "ai-actions.json", {})
    takeover_data = read_json(data_dir / "ai-takeover.json", {})

    return {
        "ticket_id_requested": ticket_id,
        "ticket_id_normalized": wanted,
        "data_dir": str(data_dir),
        "missing_evidence": missing,
        "ticket": ticket,
        "transcript": {
            "path": transcript_path,
            "chars": len(transcript or ""),
            "tail": (transcript or "")[-12000:],
        },
        "ai_usage": filter_rows(usage_rows, wanted, limit),
        "ai_feedback": filter_rows(feedback_rows, wanted, limit),
        "ai_memory_relevant": filter_rows(memory_rows, wanted, limit),
        "ai_memory_recent": memory_rows[-min(limit, 12):],
        "takeover": dict_lookup_by_ticket(takeover_data, wanted),
        "actions": dict_lookup_by_ticket(actions_data, wanted),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect Alexis ticket evidence for Hermes.")
    parser.add_argument("ticket", nargs="?", help="Ticket id, for example 0090 or #90")
    parser.add_argument("--ticket", dest="ticket_opt", help="Ticket id, for example 0090 or #90")
    parser.add_argument(
        "--data-dir",
        default=os.environ.get("ALEXIS_DATA_DIR") or DEFAULT_DATA_DIR,
        help="Alexis data directory, defaults to ALEXIS_DATA_DIR or /opt/alexis-bot/data-prod",
    )
    parser.add_argument("--limit", type=int, default=30, help="Max rows per JSONL evidence section")
    args = parser.parse_args()

    ticket = args.ticket_opt or args.ticket
    if not ticket:
        parser.error("ticket id required")

    bundle = build_bundle(Path(args.data_dir), ticket, max(1, args.limit))
    print(json.dumps(bundle, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
