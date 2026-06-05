import { NextResponse } from 'next/server';
import { DEFAULT_USER_SETTINGS } from '../../../types/userSettings';
import { normalizeUserSettings } from '../../../lib/settings/userSettingsStorage';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

function getBackendApiUrl(): string | null {
  const value = process.env.BACKEND_API_URL?.trim();

  return value ? value.replace(/\/$/, '') : null;
}

async function proxyToBackend(
  method: 'GET' | 'PUT' | 'POST',
  body?: unknown,
): Promise<Response | null> {
  const backendApiUrl = getBackendApiUrl();

  if (!backendApiUrl) {
    return null;
  }

  try {
    return await fetch(`${backendApiUrl}/api/user-settings`, {
      method,
      headers: {
        Accept: 'application/json',
        ...(body ? { 'Content-Type': 'application/json' } : {}),
      },
      body: body ? JSON.stringify(body) : undefined,
      cache: 'no-store',
    });
  } catch {
    return null;
  }
}

export async function GET() {
  const backendResponse = await proxyToBackend('GET');

  if (backendResponse?.ok) {
    return NextResponse.json(await backendResponse.json());
  }

  return NextResponse.json({
    ...DEFAULT_USER_SETTINGS,
    source: 'fallback',
    persisted: false,
  });
}

export async function PUT(request: Request) {
  const body = (await request.json().catch(() => null)) as unknown;
  const settings = normalizeUserSettings(body);
  const backendResponse = await proxyToBackend('PUT', settings);

  if (backendResponse?.ok) {
    return NextResponse.json(await backendResponse.json());
  }

  return NextResponse.json({
    ...settings,
    source: 'fallback',
    persisted: false,
  });
}

export async function POST(request: Request) {
  return PUT(request);
}
