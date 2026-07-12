import json
import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

GENERATION_PROMPT = """
Quyidagi matn asosida {num_questions} ta savol yarat. Har bir savol ABCD variantli (4 ta variant) bo'lsin va faqat bittasi to'g'ri javob bo'lsin.

Javobni FAQAT quyidagi JSON formatda qaytar, boshqa hech qanday matn, izoh yoki markdown belgisi qo'shma:

{{
  "questions": [
    {{
      "text": "savol matni",
      "choices": [
        {{"label": "A", "text": "variant matni", "is_correct": false}},
        {{"label": "B", "text": "variant matni", "is_correct": true}},
        {{"label": "C", "text": "variant matni", "is_correct": false}},
        {{"label": "D", "text": "variant matni", "is_correct": false}}
      ]
    }}
  ]
}}

Matn:
\"\"\"
{passage_text}
\"\"\"
"""

class QuestionGenerationError(Exception):
    pass


def generate_questions_from_passage(passage_text: str, num_questions: int = 5) -> list[dict]:
    model = genai.GenerativeModel(
        'gemini-3.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )

    prompt = GENERATION_PROMPT.format(
        num_questions=num_questions,
        passage_text=passage_text
    )

    try:
        response = model.generate_content(prompt)
        data = json.loads(response.text)
    except json.JSONDecodeError as e:
        raise QuestionGenerationError(f"AI javobini JSON sifatida o'qib bo'lmadi: {e}")
    except Exception as e:
        raise QuestionGenerationError(f"AI so'roviga xato: {e}")

    questions = data.get('questions', [])
    _validate_questions(questions)
    return questions

def _validate_questions(questions: list[dict]):
    """AI qaytargan har bir savolda aniq 4 ta variant va bitta to'g'ri javob borligini tekshiradi."""
    for i, q in enumerate(questions):
        choices = q.get('choices', [])
        if len(choices) != 4:
            raise QuestionGenerationError(f"{i+1}-savolda 4 ta emas, {len(choices)} ta variant bor.")
        correct_count = sum(1 for c in choices if c.get('is_correct'))
        if correct_count != 1:
            raise QuestionGenerationError(f"{i+1}-savolda to'g'ri javoblar soni noto'g'ri: {correct_count}.")