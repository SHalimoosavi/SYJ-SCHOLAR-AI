from __future__ import annotations

SYSTEM = """
You are Scholar AI.

Rules:
- Return ONLY valid JSON.
- No markdown.
- No code fences.
- No explanations.
- No text before or after JSON.
- Generate real answers from the supplied text.
""".strip()


def summarize_prompt(text: str):
    user = f"""
Read the text and create a summary.

Return JSON:

{{
  "title": "document title",
  "summary": "concise summary",
  "key_points": [
    "point 1",
    "point 2",
    "point 3"
  ]
}}

TEXT:
{text[:3000]}
"""
    return SYSTEM, user.strip()


def notes_prompt(text: str):
    user = f"""
Create study notes.

Return JSON:

{{
  "title": "topic",
  "overview": "short overview",
  "notes": [
    "note 1",
    "note 2",
    "note 3"
  ]
}}

TEXT:
{text[:3000]}
"""
    return SYSTEM, user.strip()


def flashcards_prompt(text: str):
    user = f"""
Create flashcards.

Return JSON:

{{
  "topic": "topic",
  "cards": [
    {{
      "question": "question",
      "answer": "answer"
    }}
  ]
}}

TEXT:
{text[:3000]}
"""
    return SYSTEM, user.strip()


def quiz_prompt(text: str, count: int = 5):
    user = f"""
Create {count} quiz questions.

Return JSON:

{{
  "topic": "topic",
  "questions": [
    {{
      "question": "question",
      "answer": "answer"
    }}
  ]
}}

TEXT:
{text[:3000]}
"""
    return SYSTEM, user.strip()


def exam_prompt(text: str):
    user = f"""
Create exam preparation material.

Return JSON:

{{
  "topic": "topic",
  "important_topics": [
    "topic 1",
    "topic 2"
  ],
  "possible_questions": [
    "question 1",
    "question 2"
  ]
}}

TEXT:
{text[:3000]}
"""
    return SYSTEM, user.strip()


def study_prompt(text: str):
    user = f"""
Create a complete study package.

Return JSON:

{{
  "summary": {{
    "title": "",
    "summary": ""
  }},
  "notes": [
    "note"
  ],
  "flashcards": [
    {{
      "question": "",
      "answer": ""
    }}
  ],
  "quiz": [
    {{
      "question": "",
      "answer": ""
    }}
  ]
}}

TEXT:
{text[:3000]}
"""
    return SYSTEM, user.strip()


PROMPT_MAP = {
    "summarize": summarize_prompt,
    "notes": notes_prompt,
    "flashcards": flashcards_prompt,
    "quiz": quiz_prompt,
    "exam": exam_prompt,
    "study": study_prompt,
}


def get_prompt(action: str, text: str, **kwargs):
    builder = PROMPT_MAP.get(action)

    if builder is None:
        raise ValueError(f"Unknown action: {action}")

    return builder(text, **kwargs)
