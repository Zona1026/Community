export type TrendMomentum = 'rising' | 'stable' | 'weak';

export interface TrendSignal {
  id: string;
  topicName: string;
  score: number;
  momentum: TrendMomentum;
  topics: string[];
}
