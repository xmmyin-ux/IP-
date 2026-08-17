# IP 行业每日快报

个人用、纯规则的网页电子报：每天按网文、短剧、漫剧、影游、AIGC 五栏汇总行业动态，每栏最多 12 条。

## 运行

```bash
python3 run.py --output docs
python3 -m unittest discover -s tests
```

生成后打开 `docs/index.html`。GitHub Actions 会在北京时间每天 09:00 运行；需要在仓库设置中启用 Pages 并选择 `main /docs` 发布。

## 配置

`config.json` 管理 RSS 信源、栏目、地区配额、事件关键词和重点关注清单。`social_watchlist.json` 管理 100 个公众号和小红书白名单的站内检索入口，默认不抓取其内容。第一版不使用 AI、不保存原文全文。

## 搜索记录

- 已验证 Google News 的中文“短剧”和英文“generative AI”公开 RSS 可读取，条目含标题、发布时间与来源。
- 其条款仅允许个人、非商业阅读；本项目定位为个人快报，不作商业分发。
