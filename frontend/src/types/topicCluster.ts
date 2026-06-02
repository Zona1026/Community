import type { NormalizedContent } from './normalizedContent';

export interface TopicCluster {
  id: string;
  name: string;
  platform: string;
  items: NormalizedContent[];
}
