import type { NormalizedContent } from '../types/normalizedContent';
import type { TopicCluster } from '../types/topicCluster';

export function createTopicClusters(items: NormalizedContent[]): TopicCluster[] {
  const clustersByPlatform = new Map<string, NormalizedContent[]>();

  items.forEach((item) => {
    const currentItems = clustersByPlatform.get(item.platform) ?? [];
    clustersByPlatform.set(item.platform, [...currentItems, item]);
  });

  return Array.from(clustersByPlatform.entries()).map(([platform, clusterItems]) => ({
    id: platform.toLowerCase(),
    name: `${platform} 熱門話題`,
    platform,
    items: clusterItems,
  }));
}
