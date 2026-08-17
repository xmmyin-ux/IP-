from datetime import datetime, timedelta, timezone
import unittest
from pathlib import Path
from ip_digest.core import Item, load_watchlist, normalized_link, select

class RulesTest(unittest.TestCase):
    def test_normalized_link_removes_utm(self): self.assertEqual(normalized_link("https://x.test/a/?utm_a=1&id=2"), "https://x.test/a?id=2")
    def test_selection_caps_and_deduplicates(self):
        now=datetime.now(timezone.utc); make=lambda title, region, score: Item(title, "https://x/"+title, now-timedelta(hours=1), "x", "网文", region, "", score)
        config={"regional_target":{"china":10,"overseas":2},"max_items_per_section":12}
        rows=[make(f"c{i}","china",i) for i in range(12)]+[make(f"o{i}","overseas",i) for i in range(4)]
        result=select(rows,config)["网文"]; self.assertEqual(len(result),12); self.assertEqual(sum(x.region=="overseas" for x in result),2)

    def test_social_watchlist_is_complete_and_disabled(self):
        rows = load_watchlist(Path("social_watchlist.json"))
        self.assertEqual(len(rows), 100)
        self.assertTrue(all(not row["enabled"] for row in rows))
        self.assertTrue(all(row["search_url"].startswith("https://") for row in rows))
if __name__ == "__main__": unittest.main()
