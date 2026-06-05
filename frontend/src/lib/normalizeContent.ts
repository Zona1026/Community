import type { ContentItem } from '../types/content';
import type { NormalizedContent } from '../types/normalizedContent';

export function normalizeContent(items: ContentItem[]): NormalizedContent[] {
  return items.map((item) => ({
    id: item.id,
    sourcePlatform: item.platform,
    topicTitle: item.title,
    normalizedText: item.content.trim(),
    originalUrl: item.url,
    engagementScore: item.likeCount + item.commentCount,
    hotScore: item.likeCount + item.commentCount * 2,
    hotTags: item.hotTags,
    likeCount: item.likeCount,
    commentCount: item.commentCount,
    industryTags: item.industryTags,
    keywords: item.keywords,
    createdAt: item.createdAt,
    importedAt: item.importedAt,
  }));
}
