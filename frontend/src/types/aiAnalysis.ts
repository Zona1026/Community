export type AiTone = '專業' | '輕鬆' | '犀利';

export type PostAngle = '教學' | '觀點' | '懶人包';

export type AiProvider = 'mock' | 'openai' | 'gemini';

export interface GeneratedCopy {
  id: string;
  tone: AiTone;
  angle: PostAngle;
  text: string;
  createdAt: string;
}

export interface AiAnalysis {
  shortSummary: string;
  fullSummary: string;
  controversyWarning: string;
  contentIdeas: string[];
  generatedCopies: GeneratedCopy[];
  provider?: AiProvider;
  isFallback?: boolean;
  errorMessage?: string;
}

export interface AiAnalysisInput {
  topicId: string;
  topic: string;
  score: number;
  momentum: string;
  summary: string;
  insight: string;
  source: string;
  contentCount: number;
  relatedContent: Array<{
    title: string;
    source: string;
    text: string;
  }>;
  platformTags: string[];
  topicTags: string[];
  tone: AiTone;
  angle: PostAngle;
}
