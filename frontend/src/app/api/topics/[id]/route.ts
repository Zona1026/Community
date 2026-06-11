import { NextResponse } from 'next/server';
import { getBackendApiUrl } from '../../../../lib/api/backendApiUrl';
import { buildDashboardData } from '../../../../lib/dashboard/buildDashboardData';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

async function fetchTopicFromBackend(topicId: string): Promise<Response | null> {
  try {
    return await fetch(
      `${getBackendApiUrl()}/api/topics/${encodeURIComponent(topicId)}`,
      {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
        cache: 'no-store',
      },
    );
  } catch {
    return null;
  }
}

export async function GET(
  _request: Request,
  { params }: { params: { id: string } },
) {
  const backendResponse = await fetchTopicFromBackend(params.id);

  if (backendResponse?.ok) {
    return NextResponse.json(await backendResponse.json());
  }

  const data = await buildDashboardData();
  const topic = data.allTopics.find((item) => item.id === params.id);

  if (!topic) {
    return NextResponse.json({ error: 'Topic not found.' }, { status: 404 });
  }

  return NextResponse.json(topic);
}
