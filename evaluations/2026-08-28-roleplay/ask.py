#!/usr/bin/env python3
"""Talk to the chat gateway (same /chat endpoint the web UI uses) and log
the conversation to markdown.

Usage: ask.py <role-slug> "<question>"

State per role lives in <role-slug>/conversation.json (full message
history, resent on every turn like the browser does) and the human-readable
transcript in <role-slug>/conversation.md.
"""
import json
import sys
import time
from pathlib import Path

import httpx

GATEWAY = "http://127.0.0.1:8064/chat"
BASE = Path(__file__).parent


def main():
    slug, question = sys.argv[1], sys.argv[2]
    d = BASE / slug
    d.mkdir(exist_ok=True)
    conv_path = d / "conversation.json"
    md_path = d / "conversation.md"
    conv = json.loads(conv_path.read_text()) if conv_path.exists() else []
    conv.append({"role": "user", "content": question})

    n = sum(1 for m in conv if m["role"] == "user")
    events = []
    reply = None
    t0 = time.time()
    with httpx.stream("POST", GATEWAY, json={"messages": conv}, timeout=300) as r:
        ev = None
        for line in r.iter_lines():
            if line.startswith("event: "):
                ev = line[7:].strip()
            elif line.startswith("data: ") and ev:
                data = json.loads(line[6:])
                events.append((ev, data))
                if ev == "result":
                    reply = data.get("reply", "")
                ev = None
    elapsed = time.time() - t0

    if reply is None:
        errs = [d for e, d in events if e == "error"]
        reply = "(no reply) " + json.dumps(errs, ensure_ascii=False)
    conv.append({"role": "assistant", "content": reply})
    conv_path.write_text(json.dumps(conv, ensure_ascii=False, indent=1))

    out = [f"\n## Q{n}: {question}\n"]
    for e, data in events:
        if e == "tool_call":
            out.append(f"- tool_call `{data['tool']}` {json.dumps(data.get('arguments'), ensure_ascii=False)}")
        elif e == "table":
            rows = data.get("data") or []
            out.append(f"- table: {max(len(rows) - 1, 0)} rows, header {rows[0] if rows else '[]'}")
        elif e == "chart":
            out.append("- chart")
        elif e == "force":
            out.append(f"- force: {data.get('message')}")
        elif e == "error":
            out.append(f"- ERROR: {json.dumps(data, ensure_ascii=False)}")
    out.append(f"\n**Assistant** ({elapsed:.0f}s):\n\n{reply}\n")
    with md_path.open("a") as f:
        f.write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
