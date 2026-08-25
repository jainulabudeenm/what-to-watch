#!/usr/bin/env python3
"""One runnable check for the importer. No framework on purpose.

Runs all three sources into a throwaway library and asserts the merge did what
the skill relies on: one row per title, best-known status wins, ratings land on
a 1 to 10 scale, and ids survive.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "import-history.py"
FIX = HERE / "fixtures"

failures = []


def check(desc, cond):
    if cond:
        print(f"ok   {desc}")
    else:
        print(f"FAIL {desc}")
        failures.append(desc)


def run(tmp, *files):
    env = dict(os.environ, WHAT_TO_WATCH_HOME=tmp)
    r = subprocess.run([sys.executable, str(SCRIPT), *files],
                       env=env, capture_output=True, text=True)
    return r, json.loads((Path(tmp) / "library.json").read_text())


def by_title(lib, title):
    for it in lib["items"]:
        if it["title"] == title:
            return it
    return None


with tempfile.TemporaryDirectory() as tmp:
    r, lib = run(tmp, str(FIX / "must-export.json"))
    check("must import exits 0", r.returncode == 0)
    check("must reads all three titles", len(lib["items"]) == 3)
    check("must keeps its 1 to 10 rating", by_title(lib, "The Quiet Ledger")["rating"] == 9)
    check("must keeps show episode counts",
          by_title(lib, "Harbour Lights")["episodes_watched"] == 4)
    check("must marks a show as a show", by_title(lib, "Harbour Lights")["type"] == "show")

with tempfile.TemporaryDirectory() as tmp:
    r, lib = run(tmp, str(FIX / "letterboxd-ratings.csv"),
                 str(FIX / "letterboxd-watchlist.csv"))
    check("letterboxd import exits 0", r.returncode == 0)
    check("letterboxd doubles a 4.5 star rating to 9",
          by_title(lib, "The Quiet Ledger")["rating"] == 9)
    check("letterboxd watchlist becomes want",
          by_title(lib, "Night Shift Radio")["status"] == "want")
    check("letterboxd ratings file counts as watched",
          by_title(lib, "Salt Road")["status"] == "watched")

with tempfile.TemporaryDirectory() as tmp:
    r, lib = run(tmp, str(FIX / "trakt-watched-movies.json"),
                 str(FIX / "trakt-ratings-shows.json"))
    check("trakt import exits 0", r.returncode == 0)
    check("trakt play count means watched",
          by_title(lib, "Concrete Garden")["status"] == "watched")
    check("trakt keeps the imdb id",
          by_title(lib, "Salt Road")["ids"].get("imdb") == "tt1111111")
    check("trakt show rating survives", by_title(lib, "Harbour Lights")["rating"] == 8)

# The one that actually matters: three sources, one library, no duplicates.
with tempfile.TemporaryDirectory() as tmp:
    r, lib = run(tmp,
                 str(FIX / "must-export.json"),
                 str(FIX / "letterboxd-ratings.csv"),
                 str(FIX / "letterboxd-watchlist.csv"),
                 str(FIX / "trakt-watched-movies.json"),
                 str(FIX / "trakt-ratings-shows.json"))
    titles = [i["title"] for i in lib["items"]]
    check("merged run exits 0", r.returncode == 0)
    check("no duplicate titles across sources", len(titles) == len(set(titles)))
    check("merged library has six distinct titles", len(titles) == 6)
    check("all three sources recorded",
          set(lib["sources"]) == {"must", "letterboxd", "trakt"})

    ledger = by_title(lib, "The Quiet Ledger")
    check("a title seen in two sources lists both",
          set(ledger["sources"]) == {"must", "letterboxd"})

    # Letterboxd only knows the watchlist; MUST knows he is part way through.
    # The further-along status has to win or the recommender re-suggests things.
    paper = by_title(lib, "Paper Boats")
    check("want stays want when both sources agree", paper["status"] == "want")
    harbour = by_title(lib, "Harbour Lights")
    check("watching beats want on merge", harbour["status"] == "watching")

with tempfile.TemporaryDirectory() as tmp:
    env = dict(os.environ, WHAT_TO_WATCH_HOME=tmp)
    junk = Path(tmp) / "junk.json"
    junk.write_text('{"not": "a known shape"}')
    r = subprocess.run([sys.executable, str(SCRIPT), str(junk)],
                       env=env, capture_output=True, text=True)
    check("unknown format exits non zero", r.returncode != 0)
    check("unknown format says so", "unrecognised" in r.stdout)

print()
print(f"{len(failures)} failed")
sys.exit(1 if failures else 0)
