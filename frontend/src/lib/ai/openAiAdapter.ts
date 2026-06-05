import type { AiAnalysis, AiAnalysisInput } from '../../types/aiAnalysis';

interface OpenAiResponse {
  output_text?: string;
  output?: Array<{
    content?: Array<{
      text?: string;
      type?: string;
    }>;
  }>;
}

interface OpenAiJsonResult {
  shortSummary?: unknown;
  fullSummary?: unknown;
  controversyWarning?: unknown;
  contentIdeas?: unknown;
  generatedCopy?: unknown;
}

function extractResponseText(data: OpenAiResponse): string {
  if (typeof data.output_text === 'string') {
    return data.output_text;
  }

  const text = data.output
    ?.flatMap((item) => item.content ?? [])
    .map((content) => content.text)
    .find((value): value is string => typeof value === 'string');

  return text ?? '';
}

function parseJsonResponse(text: string): OpenAiJsonResult {
  const jsonText = text
    .trim()
    .replace(/^```json/i, '')
    .replace(/^```/, '')
    .replace(/```$/, '')
    .trim();

  return JSON.parse(jsonText) as OpenAiJsonResult;
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
        '請用繁體中文分析這個趨勢話題，並只回傳可 JSON.parse 的 JSON，不要 Markdown。',
      outputSchema: {
        shortSummary: 'string',
        fullSummary: 'string',
        controversyWarning: 'string',
        contentIdeas: ['string', 'string', 'string'],
        generatedCopy: 'string',
      },
      constraints: [
        '內容適合產品 Demo 使用',
        '不要捏造不存在的資料來源',
        '爭議提醒要保守，避免過度判斷',
        'generatedCopy 需符合 tone 與 angle',
      ],
      topic: input,
    },
    null,
    2,
  );
}

export async function createOpenAiAnalysis(
  input: AiAnalysisInput,
): Promise<AiAnalysis> {
  const apiKey = process.env.OPENAI_API_KEY;

  if (!apiKey) {
    throw new Error('OPENAI_API_KEY is not configured.');
  }

  const model = process.env.OPENAI_MODEL ?? 'gpt-4o-mini';
  const response = await fetch('https://api.openai.com/v1/responses', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model,
      temperature: 0.4,
      input: [
        {
          role: 'system',
          content:
            '你是內容策略分析助理。請用繁體中文輸出精準、可讀、可 JSON.parse 的 JSON。',
        },
        {
          role: 'user',
          content: buildPrompt(input),
        },
      ],
    }),
  });

  if (!response.ok) {
    throw new Error(`OpenAI request failed with ${response.status}.`);
  }

  const data = (await response.json()) as OpenAiResponse;
  const parsed = parseJsonResponse(extractResponseText(data));
  const generatedCopy = stringValue(
    parsed.generatedCopy,
    `用${input.tone}語氣，從${input.angle}角度介紹「${input.topic}」。`,
  );

  return {
    shortSummary: stringValue(
      parsed.shortSummary,
      `${input.topic} 是目前值得追蹤的內容話題。`,
    ),
    fullSummary: stringValue(parsed.fullSummary, input.summary),
    controversyWarning: stringValue(
      parsed.controversyWarning,
      '請發布前再次確認資料來源與表述是否精準。',
    ),
    contentIdeas: stringArrayValue(parsed.contentIdeas, [
      `整理「${input.topic}」的三個重點觀察。`,
      `說明 ${input.source} 討論反映的使用者需求。`,
      `用${input.tone}語氣產出一篇${input.angle}貼文。`,
    ]),
    generatedCopies: [
      {
        id: `${input.topicId}-openai-${Date.now()}`,
        tone: input.tone,
        angle: input.angle,
        text: generatedCopy,
        createdAt: new Date().toISOString(),
      },
    ],
    provider: 'openai',
    isFallback: false,
  };
}
