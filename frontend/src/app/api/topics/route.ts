import { NextResponse } from 'next/server';
import { buildDashboardData } from '../../../lib/dashboard/buildDashboardData';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const data = await buildDashboardData();

    return NextResponse.json({
      allTopics: data.allTopics,
      industryTopics: data.industryTopics,
      userKeywordTopics: data.userKeywordTopics,
      source: 'api',
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
