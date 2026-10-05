from .services.ai_service import generate_workout


def generate_workout_gemini(
    name,
    age,
    weight,
    goal,
    intensity,
    user_id=None,
):
    return generate_workout(
        name=name,
        age=age,
        weight=weight,
        goal=goal,
        intensity=intensity,
    )