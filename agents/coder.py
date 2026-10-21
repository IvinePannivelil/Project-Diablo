import subprocess
import os

class CoderAgent:
    def __init__(self):
        self.role = "Junior Pair Programming Companion"

    def analyze_terminal_error(self, error_trace: str) -> dict:
        """Parses common Python/JS errors and suggests direct fixes."""
        suggestions = []
        if "ModuleNotFoundError" in error_trace or "No module named" in error_trace:
            suggestions.append("Missing dependency. Suggest running 'pip install <missing_module>'.")
        if "SyntaxError" in error_trace:
            suggestions.append("Check for missing colons, unbalanced parentheses, or indentation errors.")
        if "FileNotFoundError" in error_trace:
            suggestions.append("Verify the file path exists and working directory is set correctly.")
            
        return {
            "error_detected": True if suggestions else False,
            "suggestions": suggestions or ["Inspect stack trace line numbers and check parameter types."]
        }
