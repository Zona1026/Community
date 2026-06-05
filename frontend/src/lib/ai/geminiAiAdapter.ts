import type { AiAnalysis, AiAnalysisInput } from '../../types/aiAnalysis';

interface GeminiResponse {
  candidates?: Array<{
    content?: {
      parts?: Array<{
        text?: string;
      }>;
    };
  }>;
}

interface GeminiJsonResult {
  shortSummary?: unknown;
  fullSummary?: unknown;
  controversyWarning?: unknown;
  contentIdeas?: unknown;
  generatedCopy?: unknown;
}

function extractResponseText(data: GeminiResponse): string {
  return (
    data.candidates
      ?.flatMap((candidate) => candidate.content?.parts ?? [])
      .map((part) => part.text)
      .find((value): value is string => typeof value === 'string') ?? ''
  );
}

function parseJsonResponse(text: string): GeminiJsonResult {
  const jsonText = text
    .trim()
    .replace(/^```json/i, '')
    .replace(/^```/, '')
    .replace(/```$/, '')
    .trim();

  return JSON.parse(jsonText) as GeminiJsonResult;
}

function stringValue(value: unknown, fallback: string): string {
  return typeof value === 'string' && value.trim().length > 0
    ? value.trim()
    : fallback;
}

function stringArrayValue(value: unknown, fallback: string[]): string[] {
  if (!Array.isArray(value)) {
    return fallback;
  }

  const items = value.filter(
    (item): item is string => typeof item === 'string' && item.trim().length > 0,
  );

  return items.length > 0 ? items : fallback;
}

function buildPrompt(input: AiAnalysisInput): string {
  return JSON.stringify(
    {
      instruction:
        'You are a Traditional Chinese content trend analyst. Return JSON only. Do not include Markdown fences or extra prose.',
      outputSchema: {
        shortSummary: 'string',
        fullSummary: 'string',
        controversyWarning: 'string',
        contentIdeas: ['string', 'string', 'string'],
        generatedCopy: 'string',
      },
      constraints: [
        'Keep the result suitable for a demo dashboard.',
        'Base the analysis on the supplied topic and related content only.',
        'Avoid exaggeration and flag reputational or controversy risk.',
        'Make generatedCopy match the selected tone and angle.',
      ],
      topic: input,
    },
    null,
    2,
  );
}

function normalizeModelName(model: string): string {
  return model.startsWith('models/') ? model.slice('models/'.length) : model;
}

export async function createGeminiAiAnalysis(
  input: AiAnalysisInput,
): Promise<AiAnalysis> {
  const apiKey = process.env.GEMINI_API_KEY;

  if (!apiKey) {
    throw new Error('GEMINI_API_KEY is not configured.');
  }

  const model = process.env.GEMINI_MODEL ?? 'gemini-2.5-flash';
  const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${normalizeModelName(
    model,
  )}:generateContent`;
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-goog-api-key': apiKey,
    },
    body: JSON.stringify({
      contents: [
        {
          role: 'user',
          parts: [{ text: buildPrompt(input) }],
        },
      ],
      generationConfig: {
        temperature: 0.4,
        responseMimeType: 'application/json',
      },
    }),
  });

  if (!response.ok) {
    throw new Error(`Gemini request failed with ${response.status}.`);
  }

  const data = (await response.json()) as GeminiResponse;
  const parsed = parseJsonResponse(extractResponseText(data));
  const generatedCopy = stringValue(
    parsed.generatedCopy,
    `${input.tone} tone copy for ${input.topic}, using the ${input.angle} angle.`,
  );

  return {
    shortSummary: stringValue(
      parsed.shortSummary,
      `${input.topic} is gaining attention with a ${input.momentum} signal.`,
    ),
    fullSummary: stringValue(parsed.fullSummary, input.summary),
    controversyWarning: stringValue(
      parsed.controversyWarning,
      'Please verify the claims and avoid overstating the trend signal.',
    ),
    contentIdeas: stringArrayValue(parsed.contentIdeas, [
      `Explain why ${input.topic} is emerging now.`,
      `Compare ${input.source} discussion signals around ${input.topic}.`,
      `Turn ${input.topic} into a ${input.angle} post concept.`,
    ]),
    generatedCopies: [
      {
        id: `${input.topicId}-gemini-${Date.now()}`,
        tone: input.tone,
        angle: input.angle,
        text: generatedCopy,
        createdAt: new Date().toISOString(),
      },
    ],
    provider: 'gemini',
    isFallback: false,
  };
}
