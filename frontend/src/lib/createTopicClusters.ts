import type { NormalizedContent } from '../types/normalizedContent';
import type { TopicCluster } from '../types/topicCluster';

export function createTopicClusters(items: NormalizedContent[]): TopicCluster[] {
  const clustersByPlatform = new Map<string, NormalizedContent[]>();

  items.forEach((item) => {
    const currentItems = clustersByPlatform.get(item.sourcePlatform) ?? [];
    clustersByPlatform.set(item.sourcePlatform, [...currentItems, item]);
  });

  return Array.from(clustersByPlatform.entries()).map(([platform, clusterItems]) => ({
    id: platform.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''),
    name: `${platform} 熱門話題`,
    platform,
    items: clusterItems,
  }));
}
