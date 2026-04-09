from typing import Dict, Iterable, List, Optional, Union
import ast

from core.detector_utils import _public_methods, _line_range, IssueCandidate

# concern keyword groups for SRP responsibility classification
_SRP_CONCERN_GROUPS: Dict[str, List[str]] = {
    "persistence":   ["save", "load", "read", "write", "store", "fetch",
                       "insert", "delete", "update", "query", "persist",
                       "serialize", "deserialize", "export", "import"],
    "network":       ["send", "receive", "request", "response", "connect",
                       "disconnect", "upload", "download", "post", "get",
                       "http", "socket", "publish", "subscribe"],
    "presentation":  ["render", "display", "show", "format", "print",
                       "draw", "plot", "generate_html", "to_string",
                       "to_html", "to_json", "to_csv", "to_xml"],
    "validation":    ["validate", "verify", "check", "assert", "ensure",
                       "is_valid", "sanitize", "clean"],
    "computation":   ["compute", "calculate", "process", "transform",
                       "aggregate", "reduce", "apply", "run", "execute"],
    "notification":  ["notify", "alert", "email", "sms", "log", "warn",
                       "report", "broadcast"],
    "authentication":["login", "logout", "authenticate", "authorize",
                       "register", "token", "password", "permission"],
    "configuration": ["configure", "setup", "initialize", "init",
                       "reset", "config", "setting", "option"],
}

def _classify_method_concern(method_name: str) -> Optional[str]:
    """Return the concern group for a method name, or None if unclassified."""
    name_lower = method_name.lower()
    for concern, keywords in _SRP_CONCERN_GROUPS.items():
        if any(kw in name_lower for kw in keywords):
            return concern
        
    return None

def _detect_srp(tree: ast.AST) -> List[IssueCandidate]:
    candidates : List[IssueCandidate] = []
    
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        
        # Skip abstract/protocol/mixin/test classes — they legitimately
        # have many unrelated methods by design
        name_lower = node.name.lower()
        if any(skip in name_lower for skip in 
               ("abstract", "base", "mixin", "protocol", "interface",
                "test", "mock", "stub", "fake")):
            continue
        
        public_methods = _public_methods(node)
        
        # Need enough methods to meaningfully assess responsibilities
        if len(public_methods) < 4:
            continue
        
        # classify each method into a concern group
        concern_map : Dict[str, List[str]] = {}
        for method in public_methods:
            concern = _classify_method_concern(method.name)
            if concern:
                concern_map.setdefault(concern, []).append(method.name)
        
        # Only flag if methods span 2+ distinct concern groups
        if len(concern_map) < 2:
            continue
        
        # Build a human-readable summary of the mixed concerns for the LLM
        concern_summary = "; ".join(
            f"{concern}=[{', '.join(methods)}]"
            for concern, methods in concern_map.items()
        )
        
        # report at class level
        candidates.append(
            {
                "class": node.name,
                "method": public_methods[0].name,  # kept for schema compat
                "symbol_name": node.name,           # class-level, not method
                "line_range": _line_range(node),
                "principle": "SRP",
                "heuristic_summary": concern_summary,
                "srp_concern_count": len(concern_map),
            }
        )
    return candidates