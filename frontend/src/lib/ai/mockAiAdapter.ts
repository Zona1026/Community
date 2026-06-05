import type { AiAnalysis, AiAnalysisInput } from '../../types/aiAnalysis';
import { createAiAnalysis } from './createAiAnalysis';

export async function createMockAiAnalysis(
  input: AiAnalysisInput,
  errorMessage?: string,
): Promise<AiAnalysis> {
  const analysis = createAiAnalysis(input);

  return {
    ...analysis,
    provider: 'mock',
    isFallback: true,
    errorMessage,
  };
}
