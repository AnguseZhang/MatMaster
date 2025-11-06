from agents.matmaster_agent.constant import CURRENT_ENV

DocumentParserAgentName = 'document_parser_agent'

if CURRENT_ENV in ['test', 'uat']:
    DocumentParserServerUrl = 'http://pfmx1355864.bohrium.tech:50005/sse'
else:
    DocumentParserServerUrl = 'https://document-parser-uuid1758175282.app-space.dplink.cc/sse?token=4c9924cbb1b94bd5b74758a105e11024'
