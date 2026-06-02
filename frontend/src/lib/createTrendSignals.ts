import type { TopicCluster } from '../types/topicCluster';
import type { TrendMomentum, TrendSignal } from '../types/trendSignal';

function getMomentum(score: number): TrendMomentum {
  if (score >= 70) {
    return 'rising';
  }

  if (score >= 40) {
    return 'stable';
  }

  return 'weak';
}

export function createTrendSignals(clusters: TopicCluster[]): TrendSignal[] {
  return clusters.map((cluster) => {
    const score = cluster.items.length * 10;

    return {
      id: cluster.id,
      topicName: cluster.name,
      score,
      momentum: getMomentum(score),
      topics: cluster.items.map((item) => item.title),
    };
  });
}
