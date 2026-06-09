export type TrendMomentum = 'rising' | 'stable' | 'weak';
export type TrendLifecycleStage =
  | 'emerging'
  | 'growing'
  | 'mainstream'
  | 'declining';

export interface TrendPoint {
  label: string;
  score: number;
}

export interface TrendSignal {
  id: string;
  topicName: string;
  score: number;
  growthRate: number;
  momentum: TrendMomentum;
  lifecycleStage: TrendLifecycleStage;
  scoreHistory: TrendPoint[];
  topics: string[];
}
