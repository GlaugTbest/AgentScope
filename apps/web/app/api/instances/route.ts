import { NextRequest, NextResponse } from 'next/server';

const base = process.env.AGENTSCOPE_API_URL || 'http://127.0.0.1:8000';
const headers = { Authorization: `Bearer ${process.env.AGENTSCOPE_API_KEY || 'dev'}` };

export async function GET(request: NextRequest) {
  try {
    const response = await fetch(`${base}/v1/instances${request.nextUrl.search}`, { headers, cache: 'no-store' });
    return NextResponse.json(await response.json(), { status: response.status });
  } catch { return NextResponse.json({ detail: 'API unavailable' }, { status: 502 }); }
}
