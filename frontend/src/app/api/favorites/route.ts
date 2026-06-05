import { NextResponse } from 'next/server';
import { DEFAULT_FAVORITES_STATE } from '../../../types/favorites';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

function getBackendApiUrl(): string | null {
  const value = process.env.BACKEND_API_URL?.trim();

  return value ? value.replace(/\/$/, '') : null;
}

export async function GET() {
  const backendApiUrl = getBackendApiUrl();

  if (backendApiUrl) {
    try {
      const response = await fetch(`${backendApiUrl}/api/favorites`, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
        cache: 'no-store',
      });

      if (response.ok) {
        return NextResponse.json(await response.json());
      }
    } catch {
      // Keep the Demo stable with frontend fallback.
    }
  }

  return NextResponse.json(DEFAULT_FAVORITES_STATE);
}
