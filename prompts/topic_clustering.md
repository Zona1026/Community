# topic_clustering

## 目的

協助判斷多筆 NormalizedContent 是否屬於同一個 TopicCluster。

## 輸入資料

- 標題
- 內文摘要
- 平台
- 發布時間
- 關鍵字
- embedding 相似度
- 互動指標

## 判斷原則

- 是否討論同一事件
- 是否使用相同人物、品牌、地點或關鍵詞
- 是否有相似情緒或觀點
- 是否在相近時間爆發
- 是否跨平台出現相同敘事

## 輸出格式

- should_cluster
- cluster_reason
- suggested_cluster_title
- representative_keywords
- confidence
