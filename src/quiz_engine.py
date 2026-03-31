import json
from groq import Groq
from src.utils import get_groq_api_key, clean_json_response

POPULAR_SUBJECTS = [
    "Python Programming", "Java Programming", "Data Structures & Algorithms",
    "Object Oriented Programming", "Machine Learning", "Deep Learning",
    "Natural Language Processing", "Computer Networks", "Operating Systems",
    "Database Management Systems", "Web Development", "React JS",
    "Mathematics", "Physics", "Chemistry",
    "Indian History", "World History", "Geography",
    "General Knowledge", "Aptitude & Reasoning",
    "Artificial Intelligence", "Cloud Computing", "Cybersecurity",
    "Data Science", "Statistics", "Economics",
]

def get_groq_client():
    return Groq(api_key=get_groq_api_key())

def _parse_quiz_json(raw):
    raw = clean_json_response(raw)
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start != -1 and end > start:
        raw = raw[start:end]
    questions = json.loads(raw)
    validated = []
    for q in questions:
        if all(k in q for k in ["question", "options", "answer", "explanation"]):
            if isinstance(q["options"], list) and len(q["options"]) == 4:
                validated.append(q)
    return validated

def generate_quiz_from_pdf(raw_text, num_questions=10, difficulty="Medium"):
    client = get_groq_client()
    prompt = f"""Generate exactly {num_questions} MCQ questions at {difficulty} difficulty from this document.

Document:
{raw_text[:5000]}

Return ONLY a valid JSON array like this:
[
  {{
    "question": "Question text?",
    "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
    "answer": "A. option1",
    "explanation": "Why this answer is correct."
  }}
]
Return ONLY the JSON array, no other text."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=3000,
    )
    return _parse_quiz_json(response.choices[0].message.content)

def generate_quiz_from_topic(topic, num_questions=10, difficulty="Medium"):
    client = get_groq_client()
    prompt = f"""Generate exactly {num_questions} MCQ questions on "{topic}" at {difficulty} difficulty.

Return ONLY a valid JSON array like this:
[
  {{
    "question": "Question text?",
    "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
    "answer": "A. option1",
    "explanation": "Why this answer is correct."
  }}
]
Return ONLY the JSON array, no other text."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=3000,
    )
    return _parse_quiz_json(response.choices[0].message.content)

def evaluate_quiz(questions, user_answers):
    total = len(questions)
    correct = 0
    results = []
    for i, q in enumerate(questions):
        user_ans = user_answers.get(i, None)
        is_correct = user_ans == q["answer"]
        if is_correct:
            correct += 1
        results.append({
            "question": q["question"],
            "user_answer": user_ans or "Not answered",
            "correct_answer": q["answer"],
            "is_correct": is_correct,
            "explanation": q["explanation"],
            "options": q["options"],
        })
    percentage = round((correct / total) * 100) if total > 0 else 0
    if percentage >= 80:
        grade, grade_color = "Excellent", "green"
        message = "Outstanding! You have a strong grasp of this topic."
    elif percentage >= 60:
        grade, grade_color = "Good", "blue"
        message = "Good job! Review the topics you got wrong."
    elif percentage >= 40:
        grade, grade_color = "Average", "orange"
        message = "Keep practising! Focus on the explanations for wrong answers."
    else:
        grade, grade_color = "Needs Improvement", "red"
        message = "Don't give up! Review the material and try again."
    return {
        "total": total, "correct": correct, "wrong": total - correct,
        "percentage": percentage, "grade": grade,
        "grade_color": grade_color, "message": message, "results": results,
    }
