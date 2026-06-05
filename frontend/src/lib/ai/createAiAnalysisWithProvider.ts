import type {
  AiAnalysis,
  AiAnalysisInput,
  AiProvider,
} from '../../types/aiAnalysis';
import { createGeminiAiAnalysis } from './geminiAiAdapter';
import { createMockAiAnalysis } from './mockAiAdapter';
import { createOpenAiAnalysis } from './openAiAdapter';

function getConfiguredProvider(): AiProvider {
  if (process.env.AI_PROVIDER === 'openai') {
    return 'openai';
  }

  if (process.env.AI_PROVIDER === 'gemini') {
    return 'gemini';
  }

  return 'mock';
}

function getFallbackMessage(
  provider: Exclude<AiProvider, 'mock'>,
  error: unknown,
): string {
  const providerLabel = provider === 'gemini' ? 'Gemini' : 'OpenAI';

  return error instanceof Error
    ? `${providerLabel} analysis failed, using mock fallback. Reason: ${error.message}`
    : `${providerLabel} analysis failed, using mock fallback.`;
}

export async function createAiAnalysisWithProvider(
  input: AiAnalysisInput,
): Promise<AiAnalysis> {
  const provider = getConfiguredProvider();

  if (provider === 'mock') {
    return createMockAiAnalysis(input);
  }

  try {
    if (provider === 'gemini') {
      return await createGeminiAiAnalysis(input);
    }

    return await createOpenAiAnalysis(input);
  } catch (error) {
    return createMockAiAnalysis(input, getFallbackMessage(provider, error));
  }
}
