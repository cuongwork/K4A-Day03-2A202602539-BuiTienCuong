"""Check real API access without silently falling back to offline results."""
import contextlib
import io
import json
from pathlib import Path
from datetime import datetime, timezone

from app import load_test_cases, run_react_agent
from mcp_server import MCPAcademicServer
from providers import get_llm_provider


def main():
    provider = get_llm_provider()
    report = {"provider": type(provider).__name__, "model": provider.model_name,
              "run_at": datetime.now(timezone.utc).isoformat(),
              "live_api_successes": 0, "mcp_calls": 0, "api_responses": [], "tests": []}
    if report["provider"] != "OpenAIProvider":
        report["error"] = "Expected OpenAIProvider. Check LLM_PROVIDER=openai and API key."
    else:
        from openai import OpenAI
        client = OpenAI(api_key=provider.api_key, timeout=25, max_retries=0)

        class StrictProvider:
            def generate_with_tools(self, prompt, tools_schema, system_prompt=""):
                result = client.chat.completions.create(
                    model=provider.model_name,
                    temperature=0,
                    messages=[{"role": "system", "content": system_prompt},
                              {"role": "user", "content": prompt}],
                    tools=[{"type": "function", "function": s} for s in tools_schema],
                )
                report["live_api_successes"] += 1
                report["api_responses"].append({"response_id": result.id, "model": result.model,
                                               "total_tokens": result.usage.total_tokens if result.usage else None})
                msg = result.choices[0].message
                if msg.tool_calls:
                    call = msg.tool_calls[0]
                    return {"type": "tool_call", "tool_name": call.function.name,
                            "arguments": json.loads(call.function.arguments)}
                return {"type": "text", "content": msg.content or ""}

        for case in load_test_cases():
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    traces = run_react_agent(case["question"], StrictProvider(), MCPAcademicServer())
                actions = [t for t in traces if t["action_type"] == "TOOL_EXECUTION"]
                report["mcp_calls"] += len(actions)
                names = [t["tool_name"] for t in actions]
                checks = {
                    "TC01": not actions,
                    "TC02": names == ["qc_query"] and actions[0]["observation"].get("status") == "SUCCESS" if actions else False,
                    "TC03": names == ["qc_query", "create_rework_ticket"] and all(a['observation'].get('status') == 'SUCCESS' for a in actions) and actions[-1]['arguments'].get('annotation_type') == '3D' and actions[-1]['arguments'].get('severity') == 'Major' and '125' in actions[-1]['arguments'].get('error_description', ''),
                    "TC04": names == ["qc_query", "create_rework_ticket"] and all(a['observation'].get('status') == 'SUCCESS' for a in actions) and actions[-1]['arguments'].get('severity') == 'Critical' and actions[-1]['arguments'].get('annotation_type') == '3D' and '89' in actions[-1]['arguments'].get('error_description', ''),
                    "TC05": names == ["qc_query"] and actions[0]["observation"].get("status") == "NOT_FOUND" if actions else False,
                }
                final = traces[-1].get('output', '')
                final_checks = traces[-1]['action_type'] == 'FINAL_ANSWER' and bool(final.strip())
                if case['id'] == 'TC05':
                    final_checks = final_checks and 'Chưa thể xác định' in final and 'QC-INVALID-99999' in final
                if case['id'] in ('TC03', 'TC04'):
                    final_checks = final_checks and bool(actions) and actions[-1]['observation'].get('ticket_id', '__missing__') in final
                if case['id'] == 'TC01':
                    final_checks = final_checks and '2D' in final and '3D' in final and 'rework' in final.lower()
                trace_checks = all(t.get('decision_summary') and t.get('summary_source') == 'application' for t in traces)
                for action in actions:
                    schema = next(s for s in MCPAcademicServer().list_tools() if s['name'] == action['tool_name'])
                    trace_checks = trace_checks and set(action['arguments']) == set(schema['parameters']['required'])
                passed = checks.get(case['id'], False) and final_checks and trace_checks
                report["tests"].append({"id": case["id"], "tool_flow_passed": checks.get(case["id"], False),
                                        "final_answer_checks_passed": final_checks,
                                        "trace_checks_passed": trace_checks, "passed": passed,
                                        "tools": names, "traces": traces})
                print(case["id"], "PASS" if passed else "FAIL", names, flush=True)
            except Exception as error:
                # Do not print raw SDK exceptions: they can contain sensitive request details.
                report["error"] = {"type": type(error).__name__,
                                   "status": getattr(error, "status_code", None),
                                   "code": getattr(error, "code", None)}
                break
    path = Path(__file__).resolve().parent.parent / "docs" / "live_demo_check.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if len(report['tests']) == 5:
        waterfall = [dict(event, test_case_id=test['id'], provider=report['provider'],
                          model=report['model'], run_at=report['run_at'],
                          source_artifact='docs/live_demo_check.json')
                     for test in report['tests'] for event in test['traces']]
        path.with_name('trace_waterfall.json').write_text(json.dumps(waterfall, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    summary = {k: v for k, v in report.items() if k not in ("tests", "api_responses")}
    summary["tool_flow_passed"] = sum(t["tool_flow_passed"] for t in report["tests"])
    summary["tests_completed"] = len(report["tests"])
    summary["tests_passed"] = sum(t['passed'] for t in report['tests'])
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("Report:", path)
    return 0 if len(report["tests"]) == 5 and all(t["passed"] for t in report["tests"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
