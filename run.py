from __future__ import annotations
import argparse
from datetime import datetime, timezone
from pathlib import Path
from ip_digest.core import fetch_source, load_config, load_watchlist, select
from ip_digest.render import write_site

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--config", default="config.json"); parser.add_argument("--watchlist", default="social_watchlist.json"); parser.add_argument("--output", default="docs"); args = parser.parse_args()
    config = load_config(Path(args.config)); watchlist = load_watchlist(Path(args.watchlist)); now = datetime.now(timezone.utc); collected=[]; errors=[]
    for source in config["sources"]:
        items, error = fetch_source(source, now, config["window_hours"], config["event_keywords"]); collected.extend(items)
        if error: errors.append(error)
    if not collected: raise RuntimeError("所有信源均无可用条目；未覆盖现有网页。" + "；".join(errors))
    write_site(Path(args.output), now.date().isoformat(), select(collected, config), errors, watchlist)
    print(f"generated {args.output}/index.html: {len(collected)} candidates, {len(errors)} failed sources")
    return 0
if __name__ == "__main__": raise SystemExit(main())
