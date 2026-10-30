"""MCP server for Structured Output JSON Schema Guard & Repairer."""
import sys
import json
from client import StructuredJsonSchemaGuard

def handle_request(req):
    method = req.get("method")
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "validate_and_repair",
                    "description": "Autonomously repair malformed JSON and validate against expected keys and types",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "raw_output": {"type": "string"},
                            "required_keys": {"type": "array"},
                            "expected_types": {"type": "object"}
                        },
                        "required": ["raw_output"]
                    }
                }
            ]
        }
    elif method == "tools/call":
        params = req.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "validate_and_repair":
            out = StructuredJsonSchemaGuard.validate_and_repair(
                args.get("raw_output", ""),
                args.get("required_keys"),
                args.get("expected_types")
            )
            return {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]}
    return {"error": "Unsupported method or tool"}

if __name__ == "__main__":
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            print(json.dumps({"id": req.get("id"), "result": res}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()
