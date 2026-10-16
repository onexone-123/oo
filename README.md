# 运营雷达

全球运营热点、优秀品牌案例与 IP 合作方向。适配手机，支持搜索、分类筛选和浏览器本地收藏。

网站：https://onexone-123.github.io/oo/

## 每日更新

GitHub Actions 每天北京时间约 08:00（UTC 00:00）读取公开新闻 RSS，按标题去重，将数据提交至 `docs/news.json`，随后发布 GitHub Pages。GitHub 调度可能延迟。无需电脑开机，不使用付费 API。

自动更新的是新闻标题，保留原标题语言；案例与 IP 建议为人工精选，不虚构成效。来源元数据留在数据文件中便于追溯，网页不展示来源链接或面试分析。每次采集至少有一个可用的非空数据源才更新；全部失败则报错并保留上次内容。

可以在 Actions → Daily content and Pages → Run workflow 手动更新。Pages 的 Source 应选择 GitHub Actions。

## 文件

- docs/index.html：界面与响应式样式
- docs/app.js：搜索、筛选、收藏与内容呈现
- docs/news.json：自动资讯数据
- scripts/update_news.py：标准库 RSS 采集器
- .github/workflows/daily.yml：每日采集、提交、发布流程

收藏存于当前设备浏览器，不跨设备同步。公共仓库和 Pages 站点可被其他人访问。

## 看板与深度案例

首页改为四平台热榜并排的信息看板，支持展开排行、按日期回看（保留最近 30 个日期快照）、搜索和收藏。B站、抖音优先读取平台公开接口；微博使用公开接口及聚合备用服务；小红书公开热榜可能无法访问，失败时明确标记并每日重试。有旧快照时展示旧数据及原采集时间，不冒充当天结果。热度保留平台原始口径，不做跨平台相加。

`docs/cases.json` 保存精选合作研究，包括官方活动图、合作动作、视觉表达、人群分析、公开用户反应样本与商业逻辑。公开事实与编辑判断分开展示；待上市项目不宣称已取得效果。IP 方向中的建议方案不冒充已落地合作。自动 RSS 标题单独标为资讯速览，提供完整报道入口，不编造成深度案例。

相关设计、图片版权与参考项目见 `ATTRIBUTION.md` 和 `third-party/`。首页主图风格参考 Ian Xiaohei Illustrations，插画由 ImageGen 生成。
