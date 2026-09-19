import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const response = await fetch(`${process.env.AGENTSCOPE_API_URL || 'http://127.0.0.1:8000'}/v1/executions?${request.nextUrl.searchParams}`, {
      headers: { Authorization: `Bearer ${process.env.AGENTSCOPE_API_KEY || 'dev'}` }, cache: 'no-store', signal: AbortSignal.timeout(5000),
    });
    return NextResponse.json(await response.json(), { status: response.status });
  } catch { return NextResponse.json({ detail: 'API unavailable' }, { status: 502 }); }
}
