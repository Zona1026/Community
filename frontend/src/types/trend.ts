export type PlatformCode = 'threads' | 'instagram' | 'news' | 'dcard' | 'ptt';

export type LifecycleStage = 'emerging' | 'growing' | 'viral' | 'declining' | 'expired';

export type Momentum = 'rising' | 'stable' | 'cooling';

export type RiskLevel = 'low' | 'medium' | 'high';

export interface ContentItem {
  id: string;
  platformName: string;
  platformCode: PlatformCode;
  externalContentId: string;
  title: string;
  body: string;
  url: string;
  publishedAt: string;
  likes: number;
  comments: number;
  shares: number;
  contentType: string;
}

export interface Topic {
  id: string;
  topicName: string;
  summary: string;
  keywords: string[];
  representativeContents: ContentItem[];
}

export interface TrendSignal {
  heatScore: number;
  growthRate: number;
  momentum: Momentum;
  lifecycleStage: LifecycleStage;
  platforms: PlatformCode[];
  riskLevel: RiskLevel;
  riskNote: string;
}

export interface Trend extends Topic {
  heatScore: number;
  growthRate: number;
  momentum: Momentum;
  lifecycleStage: LifecycleStage;
  platforms: PlatformCode[];
  suitableIndustries: string[];
  unsuitableIndustries: string[];
  riskLevel: RiskLevel;
  riskNote: string;
  whyTrending: string;
  contentAngles: string[];
  trendSignal: TrendSignal;
}

export interface TrendReport {
  id: string;
  trendId: string;
  whyTrending: string;
  crossPlatformSummary: string;
  suitableIndustries: string[];
  unsuitableIndustries: string[];
  contentAngles: string[];
  risks: string[];
  staleRisk: RiskLevel;
}

export interface InspirationIdea {
  id: string;
  trendId: string;
  ideaTitle: string;
  ideaSummary: string;
  contentAngle: string;
  openingHook: string;
  suggestedPlatforms: string[];
  suggestedFormat: string;
  notRecommendedApproach: string;
  riskNote: string;
}

export interface InspirationForm {
  industry: string;
  brandTone: string;
  targetAudience: string;
  publishingPlatform: string;
  contentFormat: string;
}
