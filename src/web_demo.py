"""Local QC web demo. Run: python src/web_demo.py"""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

from mcp_server import MCPAcademicServer
from tools import QC_DATABASE
from app import run_react_agent
from providers import get_llm_provider


class LiveDemoProvider:
    """Real OpenAI requests only; errors never fall back to the offline mock."""
    def __init__(self):
        from openai import OpenAI
        configured = get_llm_provider()
        if configured.__class__.__name__ != 'OpenAIProvider':
            raise ValueError('Demo chat cần LLM_PROVIDER=openai và OPENAI_API_KEY hợp lệ.')
        self.model_name = configured.model_name
        self.client = OpenAI(api_key=configured.api_key, timeout=25, max_retries=0)
        self.api_calls = 0

    def generate_with_tools(self, prompt, tools_schema, system_prompt=''):
        response = self.client.chat.completions.create(
            model=self.model_name, temperature=0,
            messages=[{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': prompt}],
            tools=[{'type': 'function', 'function': s} for s in tools_schema],
            parallel_tool_calls=False,
        )
        self.api_calls += 1
        message = response.choices[0].message
        if message.tool_calls:
            call = message.tool_calls[0]
            return {'type': 'tool_call', 'tool_name': call.function.name,
                    'arguments': json.loads(call.function.arguments)}
        return {'type': 'text', 'content': message.content or ''}


class DemoAgentServer(MCPAcademicServer):
    def __init__(self):
        super().__init__()
        self.created_tickets = []

    def call_tool(self, name, arguments):
        result = super().call_tool(name, arguments)
        if name == 'create_rework_ticket' and result['result'].get('status') == 'SUCCESS':
            result['result']['ticket_id'] = f'RW-{uuid4().hex[:12].upper()}'
            self.created_tickets.append(result['result'])
        return result


class QCHandler(BaseHTTPRequestHandler):
    server_version = "QCDemo/1.0"

    def respond(self, status, content, content_type="application/json; charset=utf-8"):
        body = (json.dumps(content, ensure_ascii=False).encode("utf-8")
                if content_type.startswith("application/json") else content)
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = urlsplit(self.path).path
        if route == "/":
            self.respond(200, Path(__file__).with_name("web_demo.html").read_bytes(),
                         "text/html; charset=utf-8")
        elif route == "/api/cases":
            self.respond(200, {"cases": list(QC_DATABASE.values())})
        else:
            self.respond(404, {"error": "Không tìm thấy đường dẫn."})

    def do_POST(self):
        route = urlsplit(self.path).path
        if route not in ("/api/tool", "/api/agent"):
            self.respond(404, {"error": "Không tìm thấy đường dẫn."})
            return
        if self.headers.get("Origin") not in (None, f"http://{self.headers.get('Host')}"):
            self.respond(403, {"error": "Nguồn yêu cầu không hợp lệ."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 16384:
                raise ValueError("Yêu cầu quá dài hoặc rỗng.")
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError("Yêu cầu phải là một object JSON.")
            if route == '/api/agent':
                query = data.get('message')
                if not isinstance(query, str) or not query.strip() or len(query) > 3000:
                    raise ValueError('Nhập yêu cầu từ 1 đến 3000 ký tự.')
                provider = LiveDemoProvider()
                mcp = DemoAgentServer()
                try:
                    traces = run_react_agent(query.strip(), provider, mcp)
                    final = traces[-1] if traces else {}
                    self.respond(200, {'answer': final.get('output', 'Chưa có phản hồi.'),
                                       'completed': final.get('action_type') == 'FINAL_ANSWER',
                                       'traces': traces, 'tickets': mcp.created_tickets,
                                       'provider': 'OpenAI', 'model': provider.model_name,
                                       'api_calls': provider.api_calls,
                                       'mcp_calls': sum(t['action_type'] == 'TOOL_EXECUTION' for t in traces)})
                except Exception as error:
                    self.respond(502, {'error': 'Không hoàn tất được yêu cầu với OpenAI. Kiểm tra kết nối mạng, API key hoặc hạn mức. Không sử dụng kết quả Mock.',
                                       'error_type': type(error).__name__,
                                       'tickets': mcp.created_tickets,
                                       'api_calls': provider.api_calls})
                finally:
                    provider.client.close()
                return
            name, args = data.get("tool"), data.get("arguments")
            schemas = {s["name"]: s for s in MCPAcademicServer().list_tools()}
            if name not in ("qc_query", "create_rework_ticket") or name not in schemas:
                raise ValueError("Công cụ không được hỗ trợ.")
            if not isinstance(args, dict):
                raise ValueError("Tham số không hợp lệ.")
            schema = schemas[name]["parameters"]
            if set(args) != set(schema["required"]):
                raise ValueError("Thiếu tham số bắt buộc hoặc có tham số không được hỗ trợ.")
            for key, value in args.items():
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"{key} phải là chuỗi không rỗng.")
                if "enum" in schema["properties"][key] and value not in schema["properties"][key]["enum"]:
                    raise ValueError(f"Giá trị {key} không hợp lệ.")
            mcp = MCPAcademicServer()
            if name == "create_rework_ticket":
                lookup = mcp.call_tool("qc_query", {"qc_case_id": args["qc_case_id"]})
                case = lookup["result"].get("data")
                if not case:
                    raise ValueError("Không tìm thấy ca kiểm định.")
                if args["annotation_type"] not in {e["annotation_type"] for e in case["annotation_errors"]}:
                    raise ValueError("Ca kiểm định không có lỗi thuộc loại gán nhãn này.")
            result = mcp.call_tool(name, args)
            if name == "create_rework_ticket" and result["result"].get("status") == "SUCCESS":
                # The existing mock backend uses a deterministic ID; demo tickets need unique IDs.
                result["result"]["ticket_id"] = f"RW-{uuid4().hex[:12].upper()}"
            self.respond(200, result)
        except (ValueError, TypeError, KeyError) as error:
            self.respond(400, {"error": str(error)})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QC Assistant local web demo")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), QCHandler)
    print(f"QC Assistant: http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
