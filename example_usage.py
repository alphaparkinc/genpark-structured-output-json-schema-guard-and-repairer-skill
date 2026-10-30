"""Example usage for Structured Output JSON Schema Guard & Repairer."""
from client import StructuredJsonSchemaGuard

if __name__ == "__main__":
    raw_llm = """```json
    {
        'command': 'EXECUTE_QUERY',
        'retries': 3,
        'dry_run': false,
    }
    ```"""
    res = StructuredJsonSchemaGuard.validate_and_repair(
        raw_llm,
        required_keys=["command", "retries", "dry_run"],
        expected_types={"command": "str", "retries": "int", "dry_run": "bool"}
    )
    print("Guard Validation:", res)
