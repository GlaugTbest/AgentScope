import { NextRequest, NextResponse } from 'next/server';
const base = process.env.AGENTSCOPE_API_URL || 'http://127.0.0.1:8000';
const headers = { Authorization: `Bearer ${process.env.AGENTSCOPE_API_KEY || 'dev'}`, 'Content-Type': 'application/json' };
export async function GET() { try { const r = await fetch(`${base}/v1/agents`, { headers, cache: 'no-store' }); return NextResponse.json(await r.json(), { status: r.status }); } catch { return NextResponse.json({ detail: 'API unavailable' }, { status: 502 }); } }
export async function POST(request: NextRequest) { try { const r = await fetch(`${base}/v1/agents`, { method: 'POST', headers, body: await request.text(), cache: 'no-store' }); return NextResponse.json(await r.json(), { status: r.status }); } catch { return NextResponse.json({ detail: 'API unavailable' }, { status: 502 }); } }
