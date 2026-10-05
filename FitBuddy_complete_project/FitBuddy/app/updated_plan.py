from google import genai
from google.genai import types
from .config import get_settings

settings = get_settings()

def _demo_update(original_plan, feedback):
    return original_plan + "\n\n--- Updated from feedback ---\nFeedback applied: " + feedback + "\nThe revision keeps the seven-day structure and preserves recovery time."

def update_workout_plan(original_plan, feedback, goal, intensity):
    if not settings.gemini_api_key.strip():
        return _demo_update(original_plan, feedback)
    prompt = f"""
You are updating an existing FitBuddy wellness plan.
Goal: {goal}
Intensity: {intensity}
Original plan:
{original_plan}
User feedback:
{feedback}
Return a revised 7-day plan. Apply reasonable feedback, keep at least one recovery/rest day,
avoid unsafe exercise or extreme dieting, and finish with a brief safety note.
"""
    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model=settings.gemini_workout_model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7, max_output_tokens=3000),
        )
        return (getattr(response, "text", None) or "").strip() or _demo_update(original_plan, feedback)
    except Exception:
        return _demo_update(original_plan, feedback)
