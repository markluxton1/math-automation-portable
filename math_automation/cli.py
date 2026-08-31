from __future__ import annotations
import argparse, json
from pathlib import Path
from .store import Store

def payload(value: str) -> dict:
    return json.loads(value)

def main() -> None:
    parser = argparse.ArgumentParser(prog="math-auto")
    parser.add_argument("--root", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init"); p.add_argument("--name", required=True)
    p = sub.add_parser("artifact"); p.add_argument("type", choices=["problem","representation","evidence","literature","computation"]); p.add_argument("id"); p.add_argument("--payload", required=True); p.add_argument("--refs", default="[]")
    p = sub.add_parser("node"); p.add_argument("id"); p.add_argument("--problem", required=True)
    p = sub.add_parser("message"); p.add_argument("id"); p.add_argument("--sender", required=True); p.add_argument("--recipient", required=True); p.add_argument("--refs", required=True); p.add_argument("--comment", default="")
    p = sub.add_parser("proposal"); p.add_argument("id"); p.add_argument("--node", required=True); p.add_argument("--changes", required=True)
    p = sub.add_parser("decide"); p.add_argument("id"); p.add_argument("decision", choices=["accepted","rejected"])
    p = sub.add_parser("context"); p.add_argument("id"); p.add_argument("--node", required=True); p.add_argument("--selected", default="[]"); p.add_argument("--operation", choices=["ordinary","exploration"], required=True)
    p = sub.add_parser("dispatch"); p.add_argument("id"); p.add_argument("--context", required=True); p.add_argument("--operation", choices=["ordinary","exploration"], required=True); p.add_argument("--excluded", default="[]")
    p = sub.add_parser("invocation"); p.add_argument("id"); p.add_argument("--dispatch", required=True); p.add_argument("--output", required=True); p.add_argument("--provider", default="manual")
    sub.add_parser("validate"); sub.add_parser("history")
    a = parser.parse_args(); s = Store(a.root)
    if a.command == "init": s.init(a.name); print(a.root)
    elif a.command == "artifact": print(json.dumps(s.create_artifact(a.type,a.id,payload(a.payload),payload(a.refs)), indent=2))
    elif a.command == "node": print(json.dumps(s.create_node(a.id,a.problem), indent=2))
    elif a.command == "message": print(json.dumps(s.message(a.id,a.sender,a.recipient,payload(a.refs),a.comment), indent=2))
    elif a.command == "proposal": print(json.dumps(s.proposal(a.id,a.node,payload(a.changes)), indent=2))
    elif a.command == "decide": print(json.dumps(s.decide(a.id,a.decision), indent=2))
    elif a.command == "context": print(json.dumps(s.context(a.id,a.node,payload(a.selected),a.operation), indent=2))
    elif a.command == "dispatch": print(json.dumps(s.treatment(a.id,a.context,a.operation,payload(a.excluded)), indent=2))
    elif a.command == "invocation": print(json.dumps(s.invocation(a.id,a.dispatch,a.output,a.provider), indent=2))
    elif a.command == "validate":
        errors=s.validate(); print("VALID" if not errors else "INVALID\n"+"\n".join(errors)); raise SystemExit(bool(errors))
    else: print((a.root / "history" / "events.jsonl").read_text())

if __name__ == "__main__": main()
