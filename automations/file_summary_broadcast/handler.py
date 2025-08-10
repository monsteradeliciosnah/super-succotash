from __future__ import annotations
import os, glob, pathlib, hashlib, datetime as dt
from typing import List
from rich import print
import typer
from markdown_it import MarkdownIt
from pdfminer.high_level import extract_text
from common.logging import get_logger

log = get_logger("file_summary")
app = typer.Typer(help="Summarize new/changed files and broadcast to Slack/email.")

def sha1_bytes(b: bytes) -> str:
    import hashlib
    h = hashlib.sha1(); h.update(b); return h.hexdigest()

def summarize_text(text: str, max_words: int = 180) -> str:
    words = text.strip().split()
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]) + "..."

def extract_body(path: str) -> str:
    p = pathlib.Path(path)
    if p.suffix.lower() in {".md", ".txt"}:
        return p.read_text(errors="ignore")
    if p.suffix.lower() == ".pdf":
        return extract_text(path)
    return f"(binary file: {p.name})"

@app.command()
def main(
    folder: str = "data",
    out: str = "out.md",
    mock: bool = True,
    cache_file: str = ".broadcast_cache",
):
    folder = pathlib.Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    cache = {}
    cf = pathlib.Path(cache_file)
    if cf.exists():
        cache = {k: v for k, v in (line.strip().split(" ", 1) for line in cf.read_text().splitlines())}

    entries: List[str] = []
    for path in glob.glob(str(folder / "**/*"), recursive=True):
        p = pathlib.Path(path)
        if not p.is_file(): 
            continue
        b = p.read_bytes()
        digest = sha1_bytes(b)
        if cache.get(str(p)) == digest:
            continue
        cache[str(p)] = digest
        text = extract_body(str(p))
        summary = summarize_text(text)
        entries.append(f"### {p.name}\n\n{summary}\n")

    cf.write_text("\n".join(f"{k} {v}" for k, v in cache.items()))
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    body = f"# File Summary Broadcast ({ts})\n\n" + ("\n".join(entries) if entries else "_No changes._\n")
    pathlib.Path(out).write_text(body)
    print(f"[green]Wrote[/green] {out}")
    if not mock:
        print("[yellow]Slack/email sending is disabled in this demo. Wire your webhook here.[/yellow]")

def lambda_handler(event, context):
    main()
    return {"status": "ok"}

if __name__ == "__main__":
    app()
