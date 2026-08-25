"""Pull a public MUST profile into a json export the importer can read.

MUST has no export button. This hits the same public json API the app itself
uses, so there is no login and no key. The profile has to be public: MUST app,
settings, make profile public.

Usage:
    python3 pull-must.py <username>

Writes ~/.claude/what-to-watch/must-export-<today>.json. Feed that to
import-history.py, or just run import-history.py on it directly.
"""
import json, os, sys, time, datetime, urllib.request
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit("Usage: python3 pull-must.py <must-username>")
USERNAME = sys.argv[1]
RAW_DIR = Path(os.environ.get("WHAT_TO_WATCH_HOME",
                              Path.home() / ".claude" / "what-to-watch"))
HEADERS = {"Content-Type": "application/json", "Accept": "application/json",
           "User-Agent": "Mozilla/5.0"}  # default urllib UA is 403'd

def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def post(url, ids):
    req = urllib.request.Request(url, data=json.dumps({"ids": ids}).encode(),
                                 headers=HEADERS, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def chunks(xs, n):
    for i in range(0, len(xs), n):
        yield xs[i:i + n]

def main():
    print(f"Pulling MUST profile @{USERNAME} ...")
    u = get(f"https://mustapp.com/api/users/uri/{USERNAME}")
    if u.get("is_private"):
        sys.exit("That profile is private. Make it public in MUST settings, then retry.")
    uid = u["id"]
    L = u["lists"]
    want, watched, shows = L["want"], L["watched"], L["shows"]
    all_ids = list(dict.fromkeys(want + watched + shows))
    want_set = set(want)
    print(f"  user id {uid} | {len(all_ids)} unique titles")

    prod = {}
    for c in chunks(all_ids, 100):
        for p in post("https://mustapp.com/api/products/", c):
            prod[p["id"]] = p
        time.sleep(0.1)

    info = {}
    for c in chunks(all_ids, 100):
        for w in post(f"https://mustapp.com/api/users/id/{uid}/products/", c):
            upi = w["user_product_info"]
            info[upi["product_id"]] = upi
        time.sleep(0.1)

    items = []
    for pid in all_ids:
        p, i = prod.get(pid, {}), info.get(pid, {})
        rd = p.get("release_date") or ""
        usi = i.get("user_show_info") or {}
        rec = {"id": pid, "title": p.get("title"), "type": p.get("type"),
               "year": rd[:4] if rd else None, "release_date": rd or None,
               "status": i.get("status") or ("want" if pid in want_set else None),
               "rate": i.get("rate"), "disliked": i.get("is_disliked"),
               "reviewed": i.get("reviewed"), "runtime": p.get("runtime") or None}
        if p.get("type") == "show":
            total = p.get("items_count") or 0
            rel = p.get("items_released_count") or 0
            ew = usi.get("episodes_watched")
            rec.update({"episodes_total": total or None, "episodes_released": rel or None,
                        "episodes_watched": ew,
                        "episodes_remaining": (max(0, (rel or total) - ew) if ew is not None else None),
                        "first_unwatched_episode": usi.get("first_unwatched_episode")})
        items.append(rec)

    today = datetime.date.today().isoformat()
    out = {"meta": {"uid": uid, "uri": u.get("uri"), "name": u.get("name"), "pulled": today,
                    "hours_spent": u.get("hours_spent"), "watched_by_type": u.get("watched_by_type"),
                    "rates_statistics": u.get("rates_statistics"),
                    "top_directors": [d["person"]["name"] for d in u.get("directors", [])],
                    "top_actors": [a["person"]["name"] for a in u.get("actors", [])]},
           "items": items}
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"must-export-{today}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    wb = out["meta"]["watched_by_type"]
    print(f"  wrote {path}: {len(items)} titles "
          f"({wb.get('movies')} movies, {wb.get('shows')} shows watched; "
          f"{sum(1 for x in items if x['status']=='want')} on wishlist)")

if __name__ == "__main__":
    main()
