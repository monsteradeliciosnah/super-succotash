from __future__ import annotations
import os, math, hashlib, json
from pathlib import Path
from typing import List, Tuple
from rich import print
import typer
from common.storage import LocalStorage, FileInfo
from common.logging import get_logger

app = typer.Typer(help="Drive Clean-Up Assistant (mockable, Lambda-ready)")
log = get_logger("drive_clean_up")

def _sha1(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def scan_dir(root: str) -> List[FileInfo]:
    store = LocalStorage(root)
    infos = []
    for fi in store.list_files():
        sha = _sha1(Path(fi.path))
        infos.append(FileInfo(path=fi.path, size=fi.size, modified_ts=fi.modified_ts, sha1=sha))
    return infos

def find_duplicates(infos: List[FileInfo]) -> List[List[FileInfo]]:
    buckets = {}
    for fi in infos:
        buckets.setdefault((fi.size, fi.sha1), []).append(fi)
    return [group for group in buckets.values() if len(group) > 1]

def human_bytes(n):
    units = ["B","KB","MB","GB","TB"]
    i = 0
    while n >= 1024 and i < len(units)-1:
        n /= 1024.0; i += 1
    return f"{n:.2f} {units[i]}"

@app.command()
def main(root: str = "data", dry_run: bool = True, archive: str = "data/_Archive"):
    Path(root).mkdir(parents=True, exist_ok=True)
    Path(archive).mkdir(parents=True, exist_ok=True)
    infos = scan_dir(root)
    total_size = sum(fi.size for fi in infos)
    dups = find_duplicates(infos)

    print(f"[bold]Scanned:[/bold] {len(infos)} files; size={human_bytes(total_size)}; duplicates groups={len(dups)}")
    reclaimed = 0
    for group in dups:
        keep = group[0]
        for extra in group[1:]:
            reclaimed += extra.size
            dest = Path(archive) / Path(extra.path).name
            if dry_run:
                print(f"[yellow]Would move[/yellow] {extra.path} -> {dest}")
            else:
                Path(extra.path).replace(dest)
                print(f"[green]Moved[/green] {extra.path} -> {dest}")
    print(f"[bold magenta]Potentially reclaimable:[/bold magenta] {human_bytes(reclaimed)}")

def lambda_handler(event, context):
    # In Lambda, you'd pull a Drive/OneDrive listing via API; here we just run mock logic
    main()  # default args
    return {"status": "ok"}

if __name__ == "__main__":
    app()
