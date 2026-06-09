export interface NormalizedContent {
  id: string;
  sourcePlatform: string;
  topicTitle: string;
  normalizedText: string;
  originalUrl: string;
  engagementScore: number;
  hotScore: number;
  hotTags: string[];
  growthRate?: number;
  momentum?: 'rising' | 'stable' | 'weak';
  lifecycleStage?: 'emerging' | 'growing' | 'mainstream' | 'declining';
  scoreHistory?: Array<{
    label: string;
    score: number;
  }>;
  likeCount: number;
  commentCount: number;
  industryTags: string[];
  keywords: string[];
  createdAt: string;
  importedAt: string;
}
