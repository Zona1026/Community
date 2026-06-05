import { NextResponse } from 'next/server';
import { createAiAnalysisWithProvider } from '../../../lib/ai/createAiAnalysisWithProvider';
import type { AiAnalysisInput, AiTone, PostAngle } from '../../../types/aiAnalysis';

export const runtime = 'nodejs';

const VALID_TONES: AiTone[] = ['專業', '輕鬆', '犀利'];
const VALID_ANGLES: PostAngle[] = ['教學', '觀點', '懶人包'];

function isString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0;
}

function isAiAnalysisInput(value: unknown): value is AiAnalysisInput {
  if (!value || typeof value !== 'object') {
    return false;
  }

  const input = value as Partial<AiAnalysisInput>;

  return (
    isString(input.topicId) &&
    isString(input.topic) &&
    typeof input.score === 'number' &&
    isString(input.momentum) &&
    isString(input.summary) &&
    isString(input.insight) &&
    isString(input.source) &&
    typeof input.contentCount === 'number' &&
    Array.isArray(input.relatedContent) &&
    Array.isArray(input.platformTags) &&
    Array.isArray(input.topicTags) &&
    isString(input.tone) &&
    isString(input.angle)
  );
}

function normalizeAiInput(input: AiAnalysisInput): AiAnalysisInput {
  return {
    ...input,
    tone: VALID_TONES.includes(input.tone as AiTone)
      ? (input.tone as AiTone)
      : '專業',
    angle: VALID_ANGLES.includes(input.angle as PostAngle)
      ? (input.angle as PostAngle)
      : '教學',
  };
}

export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as unknown;

  if (!isAiAnalysisInput(body)) {
    return NextResponse.json(
      { error: 'Invalid AI analysis input.' },
      { status: 400 },
    );
  }

  const analysis = await createAiAnalysisWithProvider(normalizeAiInput(body));

  return NextResponse.json(analysis);
}
