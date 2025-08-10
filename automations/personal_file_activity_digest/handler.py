from __future__ import annotations
import os, time, random, json, pathlib, datetime as dt
from typing import List, Dict
from rich import print
import typer
from common.logging import get_logger

log = get_logger("activity_digest")
app = typer.Typer(help="Personal File Activity Digest with anomaly hints (mock).")

def synthesize_events(n=20) -> List[Dict]:
    users = ["alex", "jamie", "renee", "nicole", "kai"]
    actions = ["created", "updated", "deleted", "commented", "shared"]
    paths = ["Specs.docx", "Roadmap.md", "Q3 Plan.xlsx", "NDA.pdf", "ModelCard.md"]
    events = []
    now = time.time()
    for _ in range(n):
        events.append({
            "ts": now - random.randint(0, 86400*7),
            "user": random.choice(users),
            "action": random.choice(actions),
            "path": random.choice(paths),
            "size_delta": random.randint(-50000, 200000)
        })
    return sorted(events, key=lambda e: e["ts"], reverse=True)

def anomaly_hints(events: List[Dict]) -> List[str]:
    hints = []
    large_deletes = [e for e in events if e["action"]=="deleted" and e["size_delta"] < -20000]
    if len(large_deletes) >= 3:
        hints.append("Spike in deletions; consider reviewing recycle bin policy.")
    big_edits = [e for e in events if e["action"]=="updated" and e["size_delta"] > 150000]
    if big_edits:
        hints.append("Large updates detected; versioning might be useful to enable for this folder.")
    shares = [e for e in events if e["action"]=="shared"]
    if len(shares) > 5:
        hints.append("Unusual volume of shares; review external access rules.")
    return hints

@app.command()
def main(period: str = "daily", out: str = "digest.json"):
    events = synthesize_events()
    hints = anomaly_hints(events)
    data = {"period": period, "events": events, "insights": hints}
    pathlib.Path(out).write_text(json.dumps(data, indent=2))
    print(f"[green]Wrote[/green] {out} with {len(events)} events and {len(hints)} insights.")

def lambda_handler(event, context):
    main()
    return {"status": "ok"}

if __name__ == "__main__":
    app()
