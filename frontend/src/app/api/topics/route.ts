import { NextResponse } from 'next/server';
import { getBackendApiUrl } from '../../../lib/api/backendApiUrl';
import { buildDashboardData } from '../../../lib/dashboard/buildDashboardData';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

async function fetchTopicsFromBackend(): Promise<Response | null> {
  try {
    return await fetch(`${getBackendApiUrl()}/api/topics`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
      cache: 'no-store',
    });
  } catch {
    return null;
  }
}

export async function GET() {
  try {
    const backendResponse = await fetchTopicsFromBackend();

    if (backendResponse?.ok) {
      const backendData = await backendResponse.json();

      return NextResponse.json({
        ...backendData,
        source: backendData.source ?? 'flask-api',
      });
    }

    const data = await buildDashboardData();

    return NextResponse.json({
      allTopics: data.allTopics,
      industryTopics: data.industryTopics,
      userKeywordTopics: data.userKeywordTopics,
      source: 'next-fallback',
    });
  } catch (error) {
    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Failed to load dashboard topics.',
      },
      { status: 500 },
    );
  }
}
