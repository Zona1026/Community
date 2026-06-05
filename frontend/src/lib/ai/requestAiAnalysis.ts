import type { AiAnalysis, AiAnalysisInput } from '../../types/aiAnalysis';
import { createAiAnalysis } from './createAiAnalysis';

export async function requestAiAnalysis(
  input: AiAnalysisInput,
): Promise<AiAnalysis> {
  try {
    const response = await fetch('/api/ai-analysis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(input),
    });

    if (!response.ok) {
      throw new Error(`AI route failed with ${response.status}.`);
    }

    return (await response.json()) as AiAnalysis;
  } catch (error) {
    const fallback = createAiAnalysis(input);

    return {
      ...fallback,
      errorMessage:
        error instanceof Error
          ? `AI adapter 暫時不可用，已改用 mock fallback。原因：${error.message}`
          : 'AI adapter 暫時不可用，已改用 mock fallback。',
    };
  }
}
