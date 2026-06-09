export interface ContentItem {
  id: string;
  platform: string;
  title: string;
  content: string;
  url: string;
  likeCount: number;
  commentCount: number;
  hotTags: string[];
  growthRate?: number;
  momentum?: 'rising' | 'stable' | 'weak';
  lifecycleStage?: 'emerging' | 'growing' | 'mainstream' | 'declining';
  scoreHistory?: Array<{
    label: string;
    score: number;
  }>;
  createdAt: string;
  importedAt: string;
  industryTags: string[];
  keywords: string[];
}
