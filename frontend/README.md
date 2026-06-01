# Frontend - Trend Radar

## 產品定位

前端主頁不是社群文案產生器，也不是讓使用者一進來輸入品牌並產生貼文。

前端體驗以「趨勢雷達 / Trend Radar」為核心：

1. 發現趨勢
2. 理解趨勢
3. 評估是否適合自己的產業
4. 產生內容靈感
5. 再由使用者決定是否延伸成實際貼文

## 主頁結構

### Hero

主標題：

```text
發現正在升溫的內容趨勢
```

副標：

```text
即時追蹤社群、新聞與網路討論，找出值得跟進的話題、梗與內容靈感。
```

CTA：

- 查看今日趨勢
- 輸入產業找靈感

### Dashboard

首頁包含：

- 今日熱門趨勢
- 快速升溫趨勢
- 跨平台爆紅趨勢
- 即將過氣 / 熱度下降趨勢
- 編輯精選 / AI 推薦觀察

## 主要頁面

- `/`：趨勢雷達
- `/explore`：趨勢探索
- `/industries`：產業靈感
- `/reports`：趨勢報告
- `/saved`：收藏
- `/trends/:id`：趨勢詳情
- `/trends/:id/ideas`：內容靈感

## 核心型別

- ContentItem
- Topic
- Trend
- TrendSignal
- TrendReport
- InspirationIdea

## Mock Data

`src/data/mockTrends.ts` 目前包含 5 個趨勢：

- AI 搜尋取代傳統搜尋
- 深夜美食地圖
- 租屋壓力與居住焦慮
- 復古相機濾鏡回潮
- 名人道歉聲明模板化

## 視覺方向

使用 dashboard layout、trend card、score badge、lifecycle badge、platform chips、growth indicator 與風險提示，讓產品看起來像內容研究工具，而不是文案產生器。
