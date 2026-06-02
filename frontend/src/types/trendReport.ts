import type { TrendMomentum } from './trendSignal';

export interface TrendReport {
  id: string;
  topic: string;
  score: number;
  momentum: TrendMomentum;
  summary: string;
  evidence: string[];
  insight: string;
}
