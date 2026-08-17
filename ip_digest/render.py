from __future__ import annotations
import html
from datetime import timezone
from pathlib import Path
from .core import CATEGORIES, Item

STYLE = """<style>:root{--ink:#1e2520;--paper:#f4f0e5;--red:#a5392f;--sage:#67765a}*{box-sizing:border-box}body{margin:0;background:#253027;color:var(--ink);font-family:Georgia,'Noto Serif SC',serif}.paper{max-width:1080px;margin:36px auto;padding:44px 52px;background:var(--paper);box-shadow:12px 14px #c9c1ad,0 30px 70px #0008;background-image:radial-gradient(#0000000a 1px,transparent 1px);background-size:5px 5px}.mast{border-block:4px double var(--ink);text-align:center;padding:12px 0}.mast h1{font-size:clamp(36px,6vw,70px);margin:0}.mast p{margin:8px;color:#586057;letter-spacing:.15em}.deck{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:22px 0}.deck a{color:inherit;text-decoration:none;border-bottom:2px solid var(--red);padding:6px 0}.section{break-inside:avoid;margin:34px 0}.section h2{font-size:30px;border-bottom:3px double var(--ink);padding-bottom:7px}.grid{columns:2 320px;column-gap:34px}.article{break-inside:avoid;padding:12px 0;border-bottom:1px solid #b9b09e}.article a{color:inherit;font-size:18px;font-weight:bold;text-decoration:none}.article a:hover{color:var(--red)}.meta{font:12px system-ui,sans-serif;color:#5b6258;margin:6px 0}.article p{margin:0;line-height:1.65}.note{font:14px system-ui,sans-serif;color:#6b5640}.watchlist{margin:28px 0;padding:14px;border:1px solid #b9b09e;background:#ece6d6}.watchlist summary{cursor:pointer;font-weight:bold;font-size:20px}.watchlist-grid{columns:2 320px;column-gap:28px}.watchlist-item{break-inside:avoid;padding:9px 0;border-bottom:1px dotted #b9b09e}.watchlist-item a{color:var(--red);font:13px system-ui,sans-serif}@media(max-width:700px){.paper{margin:0;padding:28px 20px}.deck{grid-template-columns:repeat(2,1fr)}.grid,.watchlist-grid{columns:1}}</style>"""

def page(date: str, sections: dict[str, list[Item]], errors: list[str], watchlist: list[dict]) -> str:
    nav = ''.join(f'<a href="#{name}">{name}</a>' for name in CATEGORIES)
    blocks=[]
    for name in CATEGORIES:
        articles=''.join(f'<article class="article"><a href="{html.escape(x.link)}" target="_blank" rel="noopener">{html.escape(x.title)}</a><div class="meta">{html.escape(x.source)} · {x.published_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")} · {"中国" if x.region=="china" else "海外"}</div><p>{html.escape(x.summary)}</p></article>' for x in sections[name]) or '<p class="note">今日无符合规则的动态。</p>'
        blocks.append(f'<section class="section" id="{name}"><h2>{name}</h2><div class="grid">{articles}</div></section>')
    error_html = ''.join(f'<li>{html.escape(e)}</li>' for e in errors)
    watchlist_items = ''.join(f'<div class="watchlist-item"><strong>{html.escape(x["name"])}</strong> · {html.escape(x["platform"])} · {html.escape(x["type"])}<br><span class="note">{html.escape(x["category"])} · {html.escape(x["focus"])}</span> · <a href="{html.escape(x["search_url"])}" target="_blank" rel="noopener">打开搜索</a></div>' for x in watchlist)
    watchlist_html = f'<details class="watchlist"><summary>关注账号白名单 · {len(watchlist)} 个</summary><p class="note">仅作人工核验入口，尚未接入自动抓取。</p><div class="watchlist-grid">{watchlist_items}</div></details>'
    return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>IP 行业快报 {date}</title>{STYLE}</head><body><main class="paper"><header class="mast"><h1>IP 行业快报</h1><p>{date} · 每日 09:00 · 个人扫盘版</p></header><nav class="deck">{nav}</nav>{watchlist_html}{"<ul class=note>本期异常信源："+error_html+"</ul>" if errors else ""}{"".join(blocks)}<footer class="note">纯规则筛选 · 原文链接仅供个人阅读</footer></main></body></html>'

def write_site(output: Path, date: str, sections: dict[str, list[Item]], errors: list[str], watchlist: list[dict]) -> None:
    output.mkdir(parents=True, exist_ok=True); (output / "papers").mkdir(exist_ok=True)
    content = page(date, sections, errors, watchlist); (output / "index.html").write_text(content, encoding="utf-8"); (output / "papers" / f"{date}.html").write_text(content, encoding="utf-8")
    links = sorted((p.name for p in (output / "papers").glob("*.html")), reverse=True)
    archive = ''.join(f'<li><a href="papers/{x}">{x[:-5]}</a></li>' for x in links)
    (output / "archive.html").write_text(f'<!doctype html><meta charset="utf-8"><title>IP 行业快报归档</title><h1>历史快报</h1><ul>{archive}</ul>', encoding="utf-8")
