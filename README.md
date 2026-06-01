# AI 驅動的內容趨勢研究與靈感發想平台

## 專案定位

本專案不是社群文案生成器，也不是某個品牌的社群文生產器。

本專案是：

```text
AI 驅動的內容趨勢研究與靈感發想平台
```

核心目標是幫助使用者理解：

- 最近網路上紅什麼
- 哪些話題正在升溫
- 哪些內容形式正在爆
- 哪些梗、事件、議題值得關注
- 這些趨勢適合哪些產業或品牌切入
- 使用者可以如何把趨勢延伸成與自己品牌有關的內容靈感

## 核心概念

專案不以 brand 為中心，而是以以下資料為中心：

- ContentItem
- NormalizedContent
- TopicCluster
- TrendSignal
- TrendReport
- InspirationIdea

## MVP 範圍

第一版聚焦在：

- 資料匯入
- Normalize
- 去重
- Topic Clustering
- Trend Engine
- pgvector 語意相似度
- AI 趨勢分析
- AI 內容靈感發想

第一版不優先做：

- 完整品牌資料庫
- 完整 multi-tenant SaaS
- 社群平台自動發文
- 完整爬蟲系統

## 資料來源

開發階段：

- `mockData.json`

展示階段：

- 第三方工具產生的 JSON 或 CSV

進階版：

- Apify
- n8n
- 其他合法資料來源

## Trend Engine

Trend Engine 負責：

- Topic Clustering
- Growth Rate
- Momentum
- Heat Score
- Lifecycle Stage
- Cross Platform Signals
- Exploding Content Detection

## AI 角色

AI 不直接替品牌發文。

AI 用來協助使用者理解趨勢與發想內容方向：

- 這個趨勢是什麼
- 為什麼它正在紅
- 適合哪些產業切入
- 不適合哪些產業硬跟
- 可以有哪些內容角度
- 有哪些風險或過氣風險
- 有哪些可轉化成品牌內容的靈感

## 文件

- `docs/專案需求書.md`
- `docs/前端架構.md`
- `docs/後端架構.md`
- `docs/資料庫設計.md`
- `docs/開發路線圖.md`
- `docs/使用說明.md`
- `frontend/README.md`

## 前端主流程

前端主頁是「趨勢雷達 / Trend Radar」，不是文案產生器。

主要流程：

1. 發現趨勢
2. 理解趨勢
3. 評估是否適合自己的產業
4. 產生內容靈感
5. 再由使用者決定是否延伸成實際貼文

主要導覽：

- 趨勢雷達
- 趨勢探索
- 產業靈感
- 趨勢報告
- 收藏

## Prompt 管理

- `prompts/trend_analysis.md`
- `prompts/topic_clustering.md`
- `prompts/content_inspiration.md`
- `prompts/trend_report.md`
- `prompts/platform_signal_analysis.md`
