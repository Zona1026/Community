import { NextResponse } from 'next/server';
import { buildDashboardData } from '../../../../lib/dashboard/buildDashboardData';

export const dynamic = 'force-dynamic';

export async function GET(
  _request: Request,
  { params }: { params: { id: string } },
) {
  const data = await buildDashboardData();
  const topic = data.allTopics.find((item) => item.id === params.id);

  if (!topic) {
    return NextResponse.json({ error: 'Topic not found.' }, { status: 404 });
  }

  return NextResponse.json(topic);
}
