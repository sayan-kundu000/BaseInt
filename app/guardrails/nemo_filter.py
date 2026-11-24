"""NeMo Guardrails Input Security Scanner for BaseInt.

Scans incoming user natural language queries for prompt injection, tautologies,
comment expansions, and script tags prior to LLM submission.
"""

import re
from typing import Tuple, Optional

# Tautology patterns e.g. 1=1, 'a'='a', ' OR 1=1, ' OR '1'='1', WHERE 1=1
TAUTOLOGY_PATTERNS = [
    r"(?i)\b(where|or|and)\b\s+['\"]?(\w+)['\"]?\s*=\s*['\"]?\2['\"]?",
    r"(?i)\b1\s*=\s*1\b",
    r"(?i)\b0\s*=\s*0\b",
    r"(?i)\b(where|or|and)\b\s+true\b",
    r"(?i)['\"]\s*(?:or|and)\s+['\"]?1['\"]?\s*=\s*['\"]?1",
    r"(?i)['\"]\s*(?:or|and)\s+['\"]?(\w+)['\"]?\s*=\s*['\"]?\1",
]

# SQL comment expansion patterns
COMMENT_PATTERNS = [
    r"--",               # Standard SQL line comment
    r"/\*[\s\S]*?\*/",  # Standard C-style multi-line comment
    r"#[^\r\n]*",        # Shell/MySQL hash comment
]

# Script and markup injection patterns
SCRIPT_PATTERNS = [
    r"(?i)<\s*script[^>]*>",
    r"(?i)<\s*/\s*script[^>]*>",
    r"(?i)javascript\s*:",
    r"(?i)<\s*iframe[^>]*>",
    r"(?i)<\s*img[^>]+onerror[^>]*>",
]

# Destructive command patterns in raw text inputs
DESTRUCTIVE_PATTERNS = [
    r"(?i)\bdrop\s+table\b",
    r"(?i)\bdelete\s+from\b",
    r"(?i)\btruncate\s+table\b",
    r"(?i)\balter\s+table\b",
    r"(?i)\binsert\s+into\b",
    r"(?i)\bupdate\s+\w+\s+set\b",
    r"(?i)\bdrop\s+database\b",
    r"(?i)\bexec(?:ute)?\s*\(",
    r"(?i)\bunion\s+(?:all\s+)?select\b",
]


class NeMoInputGuard:
    """Input Guardrail evaluating user queries against security heuristics."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def scan(self, user_query: str) -> Tuple[bool, Optional[str]]:
        """Scan raw user query. Returns (is_safe, violation_reason)."""
        if not self.enabled:
            return True, None

        if not user_query or not user_query.strip():
            return False, "Query cannot be empty."

        # Check script / HTML tags
        for pattern in SCRIPT_PATTERNS:
            if re.search(pattern, user_query):
                return False, "NeMo Guardrail Blocked: Malicious script tags or HTML injection attempt detected."

        # Check comment expansions
        for pattern in COMMENT_PATTERNS:
            if re.search(pattern, user_query):
                return False, "NeMo Guardrail Blocked: SQL comment expansion syntax ('--', '/*') detected in user input."

        # Check tautology exploits
        for pattern in TAUTOLOGY_PATTERNS:
            if re.search(pattern, user_query):
                return False, "NeMo Guardrail Blocked: Logical tautology pattern (e.g., 'OR 1=1') detected."

        # Check explicit destructive commands in prompt
        for pattern in DESTRUCTIVE_PATTERNS:
            if re.search(pattern, user_query):
                return False, f"NeMo Guardrail Blocked: Destructive database command pattern detected in natural language input."

        return True, None


default_nemo_guard = NeMoInputGuard(enabled=True)


def scan_input_safety(user_query: str) -> Tuple[bool, Optional[str]]:
    """Convenience wrapper for raw input safety check."""
    return default_nemo_guard.scan(user_query)
