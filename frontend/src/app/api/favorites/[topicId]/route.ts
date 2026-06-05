import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

interface RouteContext {
  params: {
    topicId: string;
  };
}

function getBackendApiUrl(): string | null {
  const value = process.env.BACKEND_API_URL?.trim();

  return value ? value.replace(/\/$/, '') : null;
}

async function proxyFavoriteRequest(method: 'POST' | 'DELETE', topicId: string) {
  const backendApiUrl = getBackendApiUrl();

  if (!backendApiUrl) {
    return null;
  }

  try {
    return await fetch(
      `${backendApiUrl}/api/favorites/${encodeURIComponent(topicId)}`,
      {
        method,
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

export async function POST(_request: Request, { params }: RouteContext) {
  const response = await proxyFavoriteRequest('POST', params.topicId);

  if (response?.ok) {
    return NextResponse.json(await response.json());
  }

  return NextResponse.json({
    topicIds: [params.topicId],
    source: 'fallback',
    persisted: false,
  });
}

export async function DELETE(_request: Request, { params }: RouteContext) {
  const response = await proxyFavoriteRequest('DELETE', params.topicId);

  if (response?.ok) {
    return NextResponse.json(await response.json());
  }

  return NextResponse.json({
    topicIds: [],
    source: 'fallback',
    persisted: false,
  });
}
