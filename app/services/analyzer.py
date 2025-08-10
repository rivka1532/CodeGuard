import ast
import re

from app.services.utils import contains_hebrew, save_analysis_to_history


def analyze_code(code: str, filename: str):
    tree = ast.parse(code)
    alerts = []

    # בדיקת אורך הקובץ
    num_lines = len(code.splitlines())
    if num_lines > 200:
        alerts.append({
            "type": "Long File",
            "lines": num_lines,
            "message": f"The file has {num_lines} lines, which exceeds the recommended limit of 200."
        })

    defined_vars = set()
    used_vars = set()

    for node in ast.walk(tree):
        # פונקציות
        if isinstance(node, ast.FunctionDef):
            # אורך הפונקציה
            func_start = node.lineno
            func_end = max(
                [getattr(n, 'lineno', func_start) for n in ast.walk(node)]
            )
            func_length = func_end - func_start + 1
            if func_length > 20:
                alerts.append({
                    "type": "Long Function",
                    "function": node.name,
                    "lines": func_length,
                    "message": f"Function '{node.name}' has {func_length} lines, which exceeds 20."
                })

            # Docstring
            if not ast.get_docstring(node):
                alerts.append({
                    "type": "Missing Docstring",
                    "function": node.name,
                    "message": f"Function '{node.name}' is missing a docstring."
                })

            # שם הפונקציה בעברית
            if contains_hebrew(node.name):
                alerts.append({
                    "type": "Hebrew Identifier",
                    "identifier": node.name,
                    "message": f"The function name '{node.name}' contains Hebrew characters, which is not recommended."
                })

        # משתנים
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store):
                defined_vars.add(node.id)
            elif isinstance(node.ctx, ast.Load):
                used_vars.add(node.id)

            # שם משתנה בעברית
            if contains_hebrew(node.id):
                alerts.append({
                    "type": "Hebrew Identifier",
                    "identifier": node.id,
                    "message": f"The variable name '{node.id}' contains Hebrew characters, which is not recommended."
                })

        # פרמטרים של פונקציות
        if isinstance(node, ast.arg):
            if contains_hebrew(node.arg):
                alerts.append({
                    "type": "Hebrew Identifier",
                    "identifier": node.arg,
                    "message": f"The parameter name '{node.arg}' contains Hebrew characters, which is not recommended."
                })

    # משתנים שלא נעשה בהם שימוש
    unused_vars = defined_vars - used_vars
    for var in unused_vars:
        alerts.append({
            "type": "Unused Variable",
            "variable": var,
            "message": f"The variable '{var}' is defined but never used."
        })

    save_analysis_to_history(filename, alerts)
    return alerts
