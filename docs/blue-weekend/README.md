# 蓝色的周末 · 内容运营面试试点

Yuanyuan 的破次元恋人内容运营面试概念提案。用一个具体生活情境承接拉新，并用三篇连续事件探索留存。

## 在线与离线演示

- GitHub Pages：https://onexone-123.github.io/oo/blue-weekend/
- 页面右上角「开始演示」切换为五段演示，左右方向键翻页，Esc退出。
- 「体验样稿」中切换两种拉新素材，再选择颜色、路线与雨天行动，最后看到对应的回顾。
- 切换「独立日常」可比较内容组织方式，切换时重新开始。
- 页面末尾可打开三分钟讲稿、下载文本讲稿、下载单文件离线演示，或打印为PDF。
- offline.html 内嵌全部样式、脚本和原创SVG，无网络也能运行。外部论文和GitHub链接需要联网。

## 内容边界

角色A、台词和事件均为原创示意，并非官方角色或游戏对话。正式试点应选用现有角色并完成人设审核。所有演算人数均为示例，没有真实用户、投放、留存或付费结果。浏览器原型不调用AI、不连接游戏、不上传输入；选择仅保存在当前页面内存，刷新即重置。跨篇引用能力仅为本地脚本演示，不代表产品能力已确认。

页面依据以下一手资料区分论文发现与运营推导：

1. Gao et al. (2025), *Parasocial Interactions in Otome Games*, https://doi.org/10.17645/mac.8662
2. Zheng (2026), *Proceduralized Intimacy*, https://doi.org/10.1177/20594364261454220
3. Gong & Huang (2023), *Finding love in online games*, https://doi.org/10.1016/j.chb.2023.107681
4. 网易开发者提交的产品介绍：https://r.app.xiaomi.com/details?id=com.neteasehzyq.virtualcharacter

## 正式实验

先比较同一角色的介绍型与情境型素材，衡量首次互动转化。再将同来源新用户随机分入独立日常与连续事件两组，保持内容量、质量、更新、入口与提醒频次一致。全部分组用户进入分析；主看D7留存，跨日同角色互动为过程指标。流量不足则分两轮实施。

数据试算使用独立二项样本的Wilson分数区间与Newcombe差值区间近似，仅帮助解释不确定性；不替代样本量设计或正式统计分析。两周观察安排从上线招募起算，前置准备另计。

## 文件

- index.html：完整提案与原创SVG插画
- styles.css：响应式、演示与打印样式
- model.js：分支回顾与数据试算纯函数
- app.js：交互体验、演示导航、讲稿下载
- offline.html：可独立打开的面试备份
- build.cjs：生成offline.html（发布目录内可用 `node build.cjs`）
- verify.cjs：检查分支、统计边界和离线打包（发布目录内可用 `node verify.cjs`）

仓库使用现有GitHub Pages工作流发布docs。此页面位于docs/blue-weekend，不覆盖仓库首页或既有项目。页面无第三方运行时依赖。
