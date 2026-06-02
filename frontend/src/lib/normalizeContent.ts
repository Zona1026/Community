import type { ContentItem } from '../types/content';
import type { NormalizedContent } from '../types/normalizedContent';

export function normalizeContent(items: ContentItem[]): NormalizedContent[] {
  return items.map((item) => ({
    id: item.id,
    title: item.title,
    body: item.content,
    platform: item.source,
  }));
}
