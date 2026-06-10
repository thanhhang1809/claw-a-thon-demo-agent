"""Simple server with web UI and agent API."""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import URLError
import urllib.parse

PORT = 8501
AGENT_PORT = 8080

# Load from environment if available
LLM_MODEL = os.environ.get('LLM_MODEL', 'qwen/qwen3-5-27b')

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.path = '/index.html'
        return super().do_GET()
    
    def do_POST(self):
        if self.path == '/invocations':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8'))
            
            result = self._call_agent(payload)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def _call_agent(self, payload):
        try:
            data = json.dumps(payload).encode('utf-8')
            req = Request(
                f'http://localhost:{AGENT_PORT}/invocations',
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            with urlopen(req, timeout=5) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception:
            return self._demo_response(payload)
    
    def _demo_response(self, payload):
        category = payload.get('category', 'behavioral')
        
        if 'answer' not in payload:
            questions = {
                'behavioral': "Kể về một lần bạn vượt qua khó khăn trong công việc?",
                'technical': "Bạn thiết kế hệ thống như thế nào cho 1 triệu users?",
                'product': "Làm sao để prioritize features?"
            }
            return {
                'status': 'success',
                'question': questions.get(category, questions['behavioral']),
                'category': category,
                'message': 'Send an answer to get coaching.'
            }
        
        return {
            'status': 'success',
            'question': payload.get('question', ''),
            'category': category,
            'local_evaluation': {
                'score': 7,
                'signals_matched': ['Structure', 'Confidence'],
                'signals_missing': ['Quantifiable results', 'STAR method'],
                'feedback': 'Câu trả lời tốt! Hãy sử dụng STAR và thêm số liệu.'
            },
            'llm_coaching': {
                'enabled': True,
                'model': LLM_MODEL,
                'result': {
                    'strengths': ['Trả lời mạch lạc', 'Có kiến thức'],
                    'improvements': ['Thêm ví dụ cụ thể', 'Sử dụng STAR'],
                    'suggestion': 'Kể về một dự án cụ thể với kết quả.'
                }
            }
        }

if __name__ == '__main__':
    os.chdir('/Users/lap14649/Documents/zalopay/hackathon')
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'🚀 Server running at http://localhost:{PORT}')
    print(f'📝 Web UI: http://localhost:{PORT}/')
    server.serve_forever()
