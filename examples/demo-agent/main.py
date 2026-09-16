import argparse,sys,time
from agentscope import AgentScope
parser=argparse.ArgumentParser();parser.add_argument('--error',action='store_true');args=parser.parse_args()
scope=AgentScope(capture_content=True,raise_on_error=True)
try:
    with scope.trace('research-agent',metadata={'demo':True}) as trace:
        with trace.span(type='llm',name='generate-plan',model='gpt-example',provider='mock') as s:s.set_usage(input_tokens=120,output_tokens=80,estimated_cost='0.000040000');s.set_input({'task':'research'});s.set_output({'plan':'search'})
        with trace.span(type='tool',name='search-web'):
            with trace.span(type='retrieval',name='retrieve-document'):time.sleep(.02)
            if args.error:raise RuntimeError('Demo tool failure')
        with trace.span(type='llm',name='analyze-results') as s:s.set_usage(input_tokens=240,output_tokens=160,estimated_cost='0.000080000')
        with trace.span(type='llm',name='generate-answer') as s:s.set_usage(input_tokens=160,output_tokens=120,estimated_cost='0.000060000')
    print(f'Trace sent: {trace.trace_id}\nOpen: http://127.0.0.1:3000/traces/{trace.trace_id}')
except Exception as error:print(f'Demo failed: {error}',file=sys.stderr);raise
