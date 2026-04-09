import ast
from typing import Dict, List, Union

IssueValue = Union[str, int]
IssueCandidate = Dict[str, IssueValue]


def _public_methods(node: ast.ClassDef) -> List[ast.FunctionDef]:
    return [
        child
        for child in node.body
        if isinstance(child, ast.FunctionDef) and not child.name.startswith("_")
    ]


def _line_range(node: ast.AST) -> str:
    start = getattr(node, "lineno", 1)
    end = getattr(node, "end_lineno", start)
    return f"L{start}-L{end}"