import ast
from pathlib import Path
from typing import Dict, Iterable, List

from config import IGNORED_DIRECTORIES, SUPPORTED_EXTENSIONS
from core.llm import call_llm
from utils.file_loader import read_text_file


IssueCandidate = Dict[str, str]


def _should_skip(path: Path) -> bool:
    return any(part in IGNORED_DIRECTORIES for part in path.parts)


def _build_prompt(
    file_path: Path,
    class_name: str,
    method_name: str,
    principle: str,
    source: str,
) -> str:
    return "\n".join(
        [
            "Analyze this Python code for a SOLID design principle violation.",
            f"file: {file_path}",
            f"class: {class_name}",
            f"method: {method_name}",
            f"principle: {principle}",
            "source:",
            source,
        ]
    )


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


def _record_issue(
    issues: List[Dict[str, object]],
    file_path: Path,
    class_name: str,
    method_name: str,
    principle: str,
    source: str,
) -> None:
    prompt = _build_prompt(file_path, class_name, method_name, principle, source)
    issues.append(call_llm(prompt))


def _detect_srp(tree: ast.AST) -> List[IssueCandidate]:
    candidates: List[IssueCandidate] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            public_methods = _public_methods(node)
            if len(public_methods) >= 4:
                candidates.append({"class": node.name, "method": public_methods[0].name, "principle": "SRP"})

    return candidates


def _detect_ocp(tree: ast.AST) -> List[IssueCandidate]:
    candidates: List[IssueCandidate] = []

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        for method in [child for child in node.body if isinstance(child, ast.FunctionDef)]:
            conditional_count = sum(1 for _ in _iter_conditionals(method))
            if conditional_count >= 2:
                candidates.append({"class": node.name, "method": method.name, "principle": "OCP"})
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
                candidates.append({"class": node.name, "method": method.name, "principle": "LSP"})
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
            candidates.append({"class": node.name, "method": public_methods[0].name, "principle": "ISP"})

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
                candidates.append({"class": node.name, "method": method.name, "principle": "DIP"})
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


def detect_violations(repository_path: Path) -> List[Dict[str, object]]:
    issues: List[Dict[str, object]] = []

    for file_path in sorted(repository_path.rglob("*")):
        if file_path.suffix not in SUPPORTED_EXTENSIONS or _should_skip(file_path):
            continue

        source = read_text_file(file_path)
        if source is None:
            continue

        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        for candidate in _collect_candidates(tree):
            _record_issue(
                issues,
                file_path=file_path,
                class_name=candidate["class"],
                method_name=candidate["method"],
                principle=candidate["principle"],
                source=source,
            )

    return issues
