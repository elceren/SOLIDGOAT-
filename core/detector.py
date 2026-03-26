import ast
from pathlib import Path
from typing import Dict, Iterable, List, Union

from config import IGNORED_DIRECTORIES, SUPPORTED_EXTENSIONS
from core.llm import call_llm_batch
from utils.file_loader import read_text_file


IssueValue = Union[str, int]
IssueCandidate = Dict[str, IssueValue]


def _should_skip(path: Path) -> bool:
    return any(part in IGNORED_DIRECTORIES for part in path.parts)


def _sanitize_source(source: str) -> str:
    lines = source.splitlines()
    while lines and lines[0].startswith("# Mock refactor applied"):
        lines.pop(0)
    return "\n".join(lines)



def _public_methods(node: ast.ClassDef) -> List[ast.FunctionDef]:
    return [
        child
        for child in node.body
        if isinstance(child, ast.FunctionDef) and not child.name.startswith("_")
    ]


def _iter_calls(node: ast.AST) -> Iterable[ast.Call]:
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            yield child


def _iter_conditionals(node: ast.AST) -> Iterable[ast.If]:
    for child in ast.walk(node):
        if isinstance(child, ast.If):
            yield child



def _line_range(node: ast.AST) -> str:
    start = getattr(node, "lineno", 1)
    end = getattr(node, "end_lineno", start)
    return f"L{start}-L{end}"


def _detect_srp(tree: ast.AST) -> List[IssueCandidate]:
    candidates: List[IssueCandidate] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            public_methods = _public_methods(node)
            if len(public_methods) >= 6:
                method = public_methods[0]
                candidates.append(
                    {
                        "class": node.name,
                        "method": method.name,
                        "symbol_name": f"{node.name}.{method.name}",
                        "line_range": _line_range(method),
                        "principle": "SRP",
                    }
                )

    return candidates


def _detect_ocp(tree: ast.AST) -> List[IssueCandidate]:
    candidates: List[IssueCandidate] = []

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        for method in [child for child in node.body if isinstance(child, ast.FunctionDef)]:
            conditional_count = sum(1 for _ in _iter_conditionals(method))
            if conditional_count >= 2:
                candidates.append(
                    {
                        "class": node.name,
                        "method": method.name,
                        "symbol_name": f"{node.name}.{method.name}",
                        "line_range": _line_range(method),
                        "principle": "OCP",
                    }
                )
                break

    return candidates


def _detect_lsp(tree: ast.AST) -> List[IssueCandidate]:
    candidates: List[IssueCandidate] = []

    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or not node.bases:
            continue

        for method in [child for child in node.body if isinstance(child, ast.FunctionDef)]:
            if any(
                isinstance(statement, ast.Raise)
                or (
                    isinstance(statement, ast.Return)
                    and isinstance(statement.value, ast.Constant)
                    and statement.value.value is None
                )
                for statement in ast.walk(method)
            ):
                candidates.append(
                    {
                        "class": node.name,
                        "method": method.name,
                        "symbol_name": f"{node.name}.{method.name}",
                        "line_range": _line_range(method),
                        "principle": "LSP",
                    }
                )
                break

    return candidates


def _detect_isp(tree: ast.AST) -> List[IssueCandidate]:
    candidates: List[IssueCandidate] = []

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        public_methods = _public_methods(node)
        placeholder_methods = 0
        for method in public_methods:
            if any(
                isinstance(statement, ast.Pass)
                or (
                    isinstance(statement, ast.Raise)
                    and isinstance(statement.exc, ast.Call)
                    and isinstance(statement.exc.func, ast.Name)
                    and statement.exc.func.id == "NotImplementedError"
                )
                for statement in method.body
            ):
                placeholder_methods += 1

        if len(public_methods) >= 5 and placeholder_methods >= 2:
            method = public_methods[0]
            candidates.append(
                {
                    "class": node.name,
                    "method": method.name,
                    "symbol_name": f"{node.name}.{method.name}",
                    "line_range": _line_range(method),
                    "principle": "ISP",
                }
            )

    return candidates


def _detect_dip(tree: ast.AST) -> List[IssueCandidate]:
    candidates: List[IssueCandidate] = []

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        for method in [child for child in node.body if isinstance(child, ast.FunctionDef)]:
            concrete_instantiations = 0
            for call in _iter_calls(method):
                if isinstance(call.func, ast.Name) and call.func.id[:1].isupper():
                    concrete_instantiations += 1

            if concrete_instantiations >= 2:
                candidates.append(
                    {
                        "class": node.name,
                        "method": method.name,
                        "symbol_name": f"{node.name}.{method.name}",
                        "line_range": _line_range(method),
                        "principle": "DIP",
                    }
                )
                break

    return candidates


def _collect_candidates(tree: ast.AST) -> List[IssueCandidate]:
    detectors = [
        _detect_srp,
        _detect_ocp,
        _detect_lsp,
        _detect_isp,
        _detect_dip,
    ]
    candidates: List[IssueCandidate] = []
    for detector in detectors:
        candidates.extend(detector(tree))
    return candidates


def detect_violations(
    repository_path: Path,
    principle: str | None = None,
    scan_roots: List[Path] | None = None,
    max_violations: int | None = None,
) -> List[Dict[str, object]]:
    import time
    issues: List[Dict[str, object]] = []
    files_scanned = 0
    candidates_found = 0
    t_total = time.monotonic()

    roots = scan_roots or [repository_path]
    for root in roots:
        for file_path in sorted(root.rglob("*")):
            if file_path.suffix not in SUPPORTED_EXTENSIONS or _should_skip(file_path):
                continue

            source = read_text_file(file_path)
            if source is None:
                continue

            analysis_source = _sanitize_source(source)
            try:
                tree = ast.parse(analysis_source)
            except SyntaxError:
                print(f"  [detector] skipping {file_path.name} — SyntaxError", flush=True)
                continue

            files_scanned += 1
            file_candidates = [
                c for c in _collect_candidates(tree)
                if principle is None or str(c["principle"]) == principle
            ]

            if file_candidates:
                print(
                    f"  [detector] {file_path.name} — "
                    f"{len(file_candidates)} candidate(s): "
                    f"{[c['symbol_name'] for c in file_candidates]}",
                    flush=True,
                )

            if file_candidates:
                remaining = (
                    max_violations - len(issues)
                    if max_violations is not None
                    else len(file_candidates)
                )
                batch = file_candidates[:remaining]
                candidates_found += len(batch)
                t_issue = time.monotonic()
                results = call_llm_batch(file_path, batch, analysis_source)
                print(
                    f"  [detector] {len(results)} issue(s) recorded in {time.monotonic() - t_issue:.2f}s "
                    f"(total so far: {len(issues) + len(results)})",
                    flush=True,
                )
                issues.extend(results)

            if max_violations is not None and len(issues) >= max_violations:
                break

        if max_violations is not None and len(issues) >= max_violations:
            print(f"  [detector] reached max_violations={max_violations} — stopping early", flush=True)
            break

    print(
        f"  [detector] done — {files_scanned} files scanned, "
        f"{candidates_found} candidates, {len(issues)} issues recorded "
        f"in {time.monotonic() - t_total:.1f}s",
        flush=True,
    )
    return issues
