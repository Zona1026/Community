import type {
  TrendLifecycleStage,
  TrendMomentum,
  TrendPoint,
} from './trendSignal';

export interface TrendReport {
  id: string;
  topic: string;
  score: number;
  growthRate: number;
  momentum: TrendMomentum;
  lifecycleStage: TrendLifecycleStage;
  scoreHistory: TrendPoint[];
  summary: string;
  evidence: string[];
  insight: string;
}
