from google import genai
from google.genai import types
from ..config import get_settings

settings = get_settings()

def _client():
    if not settings.gemini_api_key.strip():
        return None
    return genai.Client(api_key=settings.gemini_api_key)

def _generate(prompt: str, model_name: str) -> str:
    client = _client()
    if client is None:
        return ""
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=3000,
        ),
    )
    return (getattr(response, "text", None) or "").strip()

def demo_workout(name, age, weight, goal, intensity):
    focus = {
        "weight loss": "full-body movement and moderate cardio",
        "muscle gain": "strength and progressive resistance",
        "general wellness": "balanced strength, cardio, mobility and recovery",
        "flexibility": "mobility, stretching and controlled movement",
    }[goal]
    days = [
        ("Day 1", f"{focus}: warm-up; 3 rounds of squats, incline push-ups and glute bridges; easy cardio; cooldown."),
        ("Day 2", "Upper body and core: warm-up; rows, incline push-ups, shoulder mobility and controlled core work; cooldown."),
        ("Day 3", "Recovery: easy walking plus gentle mobility and stretching."),
        ("Day 4", "Lower body: warm-up; squats, reverse lunges, hip hinges and calf raises; cooldown."),
        ("Day 5", "Cardio and core: warm-up; comfortable cardio intervals; controlled core exercises; cooldown."),
        ("Day 6", "Full body: 4 to 5 simple movements in controlled rounds with rest between rounds."),
        ("Day 7", "Rest and recovery: optional light walking, hydration, sleep routine and gentle stretching."),
    ]
    out = [f"FitBuddy demo plan for {name} (age {age}, {weight:g} kg)",
           f"Goal: {goal} | Intensity: {intensity}", ""]
    for day, text in days:
        out += [day, text, ""]
    out.append("Safety: Stop if exercise causes pain, dizziness, or unusual symptoms. This is general wellness information, not medical advice.")
    return "\n".join(out)

def generate_workout(name, age, weight, goal, intensity):
    prompt = f"""
You are FitBuddy, a conservative wellness-planning assistant.
Create a practical 7-day general fitness plan for:
Name: {name}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Preferred intensity: {intensity}

Return plain text with exactly seven labeled days. For every day include Focus, Warm-up,
Main workout with exercise names and sets/reps or duration, and Rest/recovery guidance.
Include at least one recovery/rest day. Avoid diagnosis, extreme calorie restriction,
unsafe exercise, or guaranteed results. End with a short safety note.
"""
    try:
        return _generate(prompt, settings.gemini_workout_model) or demo_workout(name, age, weight, goal, intensity)
    except Exception:
        return demo_workout(name, age, weight, goal, intensity)

def demo_tip(goal):
    return {
        "weight loss": "Build balanced meals with vegetables or fruit, a protein source, filling carbohydrates, and enough fluids. Aim for sustainable habits rather than extreme restriction.",
        "muscle gain": "Include a protein-rich food in regular meals, along with carbohydrates and fluids to support training and recovery. Consistent sleep also matters.",
        "general wellness": "Prioritize regular meals, a variety of foods, adequate fluids, and a consistent sleep routine. Recovery is part of fitness too.",
        "flexibility": "Hydrate regularly and pair mobility work with balanced meals and enough sleep. Gentle consistency is more useful than forcing a stretch.",
    }.get(goal, "Prioritize balanced meals, adequate fluids, regular movement, and recovery.")

def generate_tip(goal):
    prompt = f"""
Give one concise nutrition or recovery tip for the fitness goal "{goal}".
Use general wellness advice only. Avoid calorie prescriptions, diagnosis, medication advice,
extreme restriction, and guaranteed outcomes. Keep it to 2–4 sentences.
"""
    try:
        return _generate(prompt, settings.gemini_tip_model) or demo_tip(goal)
    except Exception:
        return demo_tip(goal)
