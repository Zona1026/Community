import type { TrendReport } from '../types/trendReport';
import type { TrendSignal } from '../types/trendSignal';

function getMomentumText(momentum: TrendSignal['momentum']): string {
  if (momentum === 'rising') {
    return '升溫';
  }

  if (momentum === 'stable') {
    return '穩定';
  }

  return '偏弱';
}

function createInsight(signal: TrendSignal): string {
  if (signal.momentum === 'rising') {
    return '這個主題目前訊號較強，可以優先觀察並延伸內容方向。';
  }

  if (signal.momentum === 'stable') {
    return '這個主題有一定討論度，適合持續觀察是否出現更多相關內容。';
  }

  return '這個主題目前訊號較弱，適合先保留觀察，不急著投入大量內容製作。';
}

export function createTrendReports(signals: TrendSignal[]): TrendReport[] {
  return signals.map((signal) => ({
    id: signal.id,
    topic: signal.topicName,
    score: signal.score,
    growthRate: signal.growthRate,
    momentum: signal.momentum,
    lifecycleStage: signal.lifecycleStage,
    scoreHistory: signal.scoreHistory,
    summary: `${signal.topicName} 目前有 ${signal.topics.length} 筆相關內容，趨勢狀態為${getMomentumText(signal.momentum)}。`,
    evidence: [
      `相關內容數量：${signal.topics.length} 筆`,
      `熱門分數：${signal.score}`,
      `趨勢狀態：${getMomentumText(signal.momentum)}`,
    ],
    insight: createInsight(signal),
  }));
}
