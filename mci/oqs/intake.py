# -*- coding: utf-8 -*-
import uuid

def normalize_problem(problem_text: str) -> dict:
    return {
        "problem_id": f"prob-{uuid.uuid4().hex[:8]}",
        "raw_text": problem_text,
        "clean_text": problem_text.strip(),
        "length": len(problem_text)
    }
