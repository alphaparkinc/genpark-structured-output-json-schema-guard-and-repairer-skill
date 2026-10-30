"""Structured Output JSON Schema Guard & Repairer.
100% Python Standard Library.
"""

import json
import re

class StructuredJsonSchemaGuard:
    """Enforces strict JSON schema validation and autonomously repairs malformed JSON syntax."""

    @staticmethod
    def repair_json_string(malformed_json: str) -> str:
        s = malformed_json.strip()
        if s.startswith("```json"):
            s = s[7:]
        elif s.startswith("```"):
            s = s[3:]
        if s.endswith("```"):
            s = s[:-3]
        s = s.strip()

        # Fix trailing commas in objects and arrays
        s = re.sub(r",\s*([\]}])", r"\1", s)

        # Fix single-quoted JSON properties/strings to double quotes
        s = re.sub(r"'([^']*)'", r'"\1"', s)

        open_braces = s.count("{") - s.count("}")
        open_brackets = s.count("[") - s.count("]")
        if open_brackets > 0:
            s += "]" * open_brackets
        if open_braces > 0:
            s += "}" * open_braces

        return s

    @classmethod
    def validate_and_repair(cls, raw_output: str, required_keys: list = None, expected_types: dict = None) -> dict:
        req_keys = required_keys or []
        exp_types = expected_types or {}

        repaired_str = cls.repair_json_string(raw_output)
        parsed_obj = None
        parse_success = False
        error_msg = None

        try:
            parsed_obj = json.loads(repaired_str)
            parse_success = True
        except Exception as e:
            error_msg = str(e)

        if not parse_success or not isinstance(parsed_obj, dict):
            return {
                "status": "PARSE_FAILURE",
                "error": error_msg or "Output is not a valid JSON dictionary",
                "repaired_raw_string": repaired_str,
                "is_valid": False
            }

        missing_keys = [k for k in req_keys if k not in parsed_obj]
        type_mismatches = []

        type_map = {
            "str": str,
            "int": int,
            "float": (int, float),
            "bool": bool,
            "list": list,
            "dict": dict
        }

        for k, expected_t in exp_types.items():
            if k in parsed_obj:
                target_cls = type_map.get(expected_t)
                if target_cls and not isinstance(parsed_obj[k], target_cls):
                    type_mismatches.append(f"{k}: expected {expected_t}, got {type(parsed_obj[k]).__name__}")

        is_valid = (len(missing_keys) == 0) and (len(type_mismatches) == 0)

        return {
            "status": "VALID" if is_valid else "SCHEMA_DEFECT",
            "is_valid": is_valid,
            "parsed_payload": parsed_obj,
            "missing_required_keys": missing_keys,
            "type_mismatches": type_mismatches
        }
