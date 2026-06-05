export interface NormalizedContent {
  id: string;
  sourcePlatform: string;
  topicTitle: string;
  normalizedText: string;
  originalUrl: string;
  engagementScore: number;
  hotScore: number;
  hotTags: string[];
  likeCount: number;
  commentCount: number;
  industryTags: string[];
  keywords: string[];
  createdAt: string;
  importedAt: string;
}
