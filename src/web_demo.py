"""Local QC web demo. Run: python src/web_demo.py"""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

from mcp_server import MCPAcademicServer
from tools import QC_DATABASE


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
        if urlsplit(self.path).path != "/api/tool":
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
