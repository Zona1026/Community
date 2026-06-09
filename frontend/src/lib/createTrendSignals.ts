import type { TopicCluster } from '../types/topicCluster';
import type { TrendMomentum, TrendPoint, TrendSignal } from '../types/trendSignal';

function getMomentum(score: number): TrendMomentum {
  if (score >= 70) {
    return 'rising';
  }

  if (score >= 40) {
    return 'stable';
  }

  return 'weak';
}

function getGrowthRate(score: number): number {
  if (score >= 70) {
    return 36;
  }

  if (score >= 40) {
    return 18;
  }

  return 6;
}

function createFallbackScoreHistory(score: number): TrendPoint[] {
  return [
    { label: 'Week 1', score: Math.max(0, score - 12) },
    { label: 'Week 2', score: Math.max(0, score - 8) },
    { label: 'Week 3', score: Math.max(0, score - 4) },
    { label: 'Week 4', score },
  ];
}

export function createTrendSignals(clusters: TopicCluster[]): TrendSignal[] {
  return clusters.map((cluster) => {
    const score = cluster.items.length * 10;
    const growthRates = cluster.items
      .map((item) => item.growthRate)
      .filter((growthRate): growthRate is number =>
        Number.isFinite(growthRate),
      );
    const growthRate =
      growthRates.length > 0
        ? Math.round(
            growthRates.reduce((sum, item) => sum + item, 0) /
              growthRates.length,
          )
        : getGrowthRate(score);
    const momentum =
      cluster.items.find((item) => item.momentum)?.momentum ??
      getMomentum(score);
    const lifecycleStage =
      cluster.items.find((item) => item.lifecycleStage)?.lifecycleStage ??
      'emerging';
    const scoreHistory =
      cluster.items.find((item) => item.scoreHistory)?.scoreHistory ??
      createFallbackScoreHistory(score);

    return {
      id: cluster.id,
      topicName: cluster.name,
      score,
      growthRate,
      momentum,
      lifecycleStage,
      scoreHistory,
      topics: cluster.items.map((item) => item.topicTitle),
    };
  });
}
