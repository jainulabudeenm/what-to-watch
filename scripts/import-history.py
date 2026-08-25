#!/usr/bin/env python3
"""Turn a watch-history export into the one file the what-to-watch skill reads.

Supported sources, all detected from the file itself, no flags needed:

  MUST         a .json export (see pull-must.py, which makes one for you)
  Letterboxd   the .csv files inside the export zip: watched, ratings,
               watchlist, diary
  Trakt        .json arrays in the shape the Trakt API returns, which is what
               every Trakt export tool produces

Usage:
    python3 import-history.py <file> [<file> ...]
    python3 import-history.py ~/Downloads/letterboxd-export/*.csv

Merges everything you pass into ~/.claude/what-to-watch/library.json, keyed on
title plus year, so running two sources gives you one combined library rather
than two half libraries. Ratings are normalised to a 1 to 10 scale.
"""
import csv
import json
import os
import re
import sys
from pathlib import Path

# Override the destination in tests, or to keep a second library.
HOME_DIR = Path(os.environ.get("WHAT_TO_WATCH_HOME",
                               Path.home() / ".claude" / "what-to-watch"))
OUT = HOME_DIR / "library.json"

# When two sources disagree, the one that says you got further through it wins.
# None means the source made no claim, so it never overwrites a real status.
STATUS_RANK = {None: -1, "want": 0, "watching": 1, "watched": 2}


def key(title, year):
    t = re.sub(r"[^a-z0-9]+", "", (title or "").lower())
    return (t, year or 0)


def blank(title, year, kind):
    return {
        "title": title,
        "year": year,
        "type": kind,
        "status": "want",
        "rating": None,
        "runtime": None,
        "episodes_watched": None,
        "episodes_total": None,
        "ids": {},
        "sources": [],
    }


def merge(lib, item, source):
    k = key(item["title"], item["year"])
    cur = lib.get(k)
    if cur is None:
        cur = blank(item["title"], item["year"], item["type"])
        lib[k] = cur
    if STATUS_RANK.get(item["status"], -1) > STATUS_RANK.get(cur["status"], -1):
        cur["status"] = item["status"]
    for f in ("rating", "runtime", "episodes_watched", "episodes_total"):
        if item.get(f) is not None:
            cur[f] = item[f]
    if item["type"] == "show":
        cur["type"] = "show"
    cur["ids"].update(item.get("ids") or {})
    if source not in cur["sources"]:
        cur["sources"].append(source)


def read_must(data):
    """MUST export. rate is already 1 to 10."""
    for it in data.get("items", []):
        yield {
            "title": it.get("title"),
            "year": int(it["year"]) if str(it.get("year") or "").isdigit() else None,
            "type": "show" if it.get("type") == "show" else "movie",
            "status": it.get("status") or "want",
            "rating": it.get("rate"),
            "runtime": it.get("runtime"),
            "episodes_watched": it.get("episodes_watched"),
            "episodes_total": it.get("episodes_total"),
            "ids": {},
        }


def read_trakt(data):
    """Trakt API shaped arrays: watched, watchlist, ratings, collection."""
    for row in data:
        node = row.get("movie") or row.get("show") or {}
        if not node.get("title"):
            continue
        kind = "show" if "show" in row else "movie"
        # A play is proof you watched it. A rating is not, at least not for a
        # show: you can rate a series four episodes in. So a ratings-only row
        # makes no status claim and defers to whatever source knows better.
        if row.get("plays") or row.get("last_watched_at"):
            status = "watched"
        elif row.get("rating") is not None:
            status = None
        else:
            status = "want"
        ids = {k: v for k, v in (node.get("ids") or {}).items()
               if k in ("imdb", "tmdb", "tvdb", "slug") and v}
        yield {
            "title": node["title"],
            "year": node.get("year"),
            "type": kind,
            "status": status,
            "rating": row.get("rating"),
            "runtime": None,
            "episodes_watched": None,
            "episodes_total": None,
            "ids": ids,
        }


def read_letterboxd(rows, filename):
    """Letterboxd CSVs. Rating is 0.5 to 5.0 in half steps, so it doubles to 1 to 10."""
    name = filename.lower()
    status = "want" if "watchlist" in name else "watched"
    for r in rows:
        title = r.get("Name") or r.get("Title")
        if not title:
            continue
        raw = r.get("Rating")
        rating = None
        if raw:
            try:
                rating = int(round(float(raw) * 2))
            except ValueError:
                rating = None
        year = r.get("Year")
        ids = {}
        if r.get("Letterboxd URI"):
            ids["letterboxd"] = r["Letterboxd URI"]
        yield {
            "title": title,
            "year": int(year) if str(year or "").isdigit() else None,
            "type": "movie",  # Letterboxd is films only
            "status": status,
            "rating": rating,
            "runtime": None,
            "episodes_watched": None,
            "episodes_total": None,
            "ids": ids,
        }


def detect_and_read(path, lib):
    """Sniff the file. Returns the source name, or None if it is not one we know."""
    p = Path(path)
    text = p.read_text(encoding="utf-8-sig", errors="replace")

    if p.suffix.lower() == ".csv":
        rows = list(csv.DictReader(text.splitlines()))
        if not rows:
            return None
        if "Letterboxd URI" in rows[0] or ("Name" in rows[0] and "Year" in rows[0]):
            for item in read_letterboxd(rows, p.name):
                merge(lib, item, "letterboxd")
            return "letterboxd"
        return None

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None

    if isinstance(data, dict) and "items" in data:
        for item in read_must(data):
            merge(lib, item, "must")
        return "must"

    if isinstance(data, list) and data and isinstance(data[0], dict) and (
        "movie" in data[0] or "show" in data[0]
    ):
        for item in read_trakt(data):
            merge(lib, item, "trakt")
        return "trakt"

    return None


def main(argv):
    paths = argv[1:]
    if not paths:
        print(__doc__)
        return 2

    lib = {}
    if OUT.exists():
        for it in json.loads(OUT.read_text())["items"]:
            lib[key(it["title"], it["year"])] = it

    seen = []
    for path in paths:
        if not os.path.isfile(path):
            print(f"skip, not a file: {path}")
            continue
        src = detect_and_read(path, lib)
        if src is None:
            print(f"skip, unrecognised format: {path}")
        else:
            print(f"read {src:<11} {path}")
            seen.append(src)

    if not seen:
        print("\nNothing imported. Pass a MUST json, a Letterboxd csv, or a Trakt json.")
        return 1

    items = sorted(lib.values(), key=lambda i: (i["title"] or "").lower())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"sources": sorted(set(seen)), "items": items}, indent=1))

    counts = {}
    for it in items:
        counts[it["status"]] = counts.get(it["status"], 0) + 1
    rated = sum(1 for it in items if it["rating"] is not None)
    print(f"\nwrote {OUT}")
    print(f"  {len(items)} titles, {rated} rated")
    for status in ("watched", "watching", "want"):
        if status in counts:
            print(f"  {counts[status]} {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
