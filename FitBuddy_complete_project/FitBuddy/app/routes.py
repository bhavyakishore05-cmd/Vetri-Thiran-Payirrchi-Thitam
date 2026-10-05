from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from .database import get_db
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .models import Plan, User
from .schemas import FeedbackRequest, PlanResponse, UserInput, UserSummary
from .updated_plan import update_workout_plan

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def row(user, plan):
    return {
        "user_id": user.user_id, "name": user.name, "age": user.age,
        "weight": user.weight, "goal": user.goal, "intensity": user.intensity,
        "original_plan": plan.original_plan if plan else "",
        "updated_plan": plan.updated_plan if plan else None,
        "feedback": plan.feedback if plan else None,
    }

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"title": "FitBuddy"})

@router.get("/health")
def health():
    return {"status": "ok", "service": "FitBuddy"}

@router.get("/api/health")
def api_health():
    return {"status": "ok", "service": "FitBuddy", "database": "sqlite"}

def save_plan(db, payload, workout, tip):
    plan = db.scalar(select(Plan).where(Plan.user_id == payload.user_id))
    if plan is None:
        plan = Plan(user_id=payload.user_id, original_plan=workout, nutrition_tip=tip)
        db.add(plan)
    else:
        plan.original_plan = workout
        plan.updated_plan = None
        plan.feedback = None
        plan.nutrition_tip = tip
    return plan

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout_form(request: Request, name: str = Form(...), user_id: str = Form(...),
                          age: int = Form(...), weight: float = Form(...),
                          goal: str = Form(...), intensity: str = Form(...),
                          db: Session = Depends(get_db)):
    try:
        payload = UserInput(name=name.strip(), user_id=user_id.strip(), age=age, weight=weight, goal=goal, intensity=intensity)
    except Exception as exc:
        return templates.TemplateResponse(request=request, name="error.html",
            context={"title": "Invalid input", "message": str(exc)}, status_code=422)
    user = db.scalar(select(User).where(User.user_id == payload.user_id))
    if user is None:
        user = User(**payload.model_dump())
        db.add(user)
    else:
        for key, value in payload.model_dump().items():
            setattr(user, key, value)
    workout = generate_workout_gemini(**payload.model_dump())
    tip = generate_nutrition_tip_with_flash(payload.goal)
    plan = save_plan(db, payload, workout, tip)
    db.commit()
    return templates.TemplateResponse(request=request, name="result.html",
        context={"title": "Your FitBuddy Plan", "user": user, "plan": plan,
                 "display_plan": plan.original_plan, "is_updated": False})

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback_form(request: Request, user_id: str = Form(...), feedback: str = Form(...),
                         db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.user_id == user_id))
    plan = db.scalar(select(Plan).where(Plan.user_id == user_id))
    if user is None or plan is None:
        return templates.TemplateResponse(request=request, name="error.html",
            context={"title": "User not found", "message": "Generate a plan for this User ID first."}, status_code=404)
    feedback_model = FeedbackRequest(feedback=feedback.strip())
    revised = update_workout_plan(plan.original_plan, feedback_model.feedback, user.goal, user.intensity)
    plan.updated_plan = revised
    plan.feedback = feedback_model.feedback
    db.commit()
    return templates.TemplateResponse(request=request, name="result.html",
        context={"title": "Updated FitBuddy Plan", "user": user, "plan": plan,
                 "display_plan": revised, "is_updated": True})

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    plans = {p.user_id: p for p in db.scalars(select(Plan)).all()}
    return templates.TemplateResponse(request=request, name="all_users.html",
        context={"title": "All Users", "users": [row(u, plans.get(u.user_id)) for u in users]})

@router.post("/delete-user/{user_id}")
def delete_user_form(user_id: str, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.user_id == user_id))
    plan = db.scalar(select(Plan).where(Plan.user_id == user_id))
    if plan: db.delete(plan)
    if user: db.delete(user)
    db.commit()
    return RedirectResponse("/view-all-users", status_code=303)

@router.post("/api/plans", response_model=PlanResponse)
def api_generate_plan(payload: UserInput, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.user_id == payload.user_id))
    if user is None:
        user = User(**payload.model_dump())
        db.add(user)
    else:
        for key, value in payload.model_dump().items():
            setattr(user, key, value)
    workout = generate_workout_gemini(**payload.model_dump())
    tip = generate_nutrition_tip_with_flash(payload.goal)
    save_plan(db, payload, workout, tip)
    db.commit()
    return PlanResponse(user_id=payload.user_id, name=payload.name, goal=payload.goal,
                        intensity=payload.intensity, workout_plan=workout,
                        nutrition_tip=tip, updated=False)

@router.post("/api/plans/{user_id}/feedback", response_model=PlanResponse)
def api_feedback(user_id: str, payload: FeedbackRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.user_id == user_id))
    plan = db.scalar(select(Plan).where(Plan.user_id == user_id))
    if user is None or plan is None:
        raise HTTPException(status_code=404, detail="User or plan not found")
    revised = update_workout_plan(plan.original_plan, payload.feedback, user.goal, user.intensity)
    plan.updated_plan = revised
    plan.feedback = payload.feedback
    db.commit()
    return PlanResponse(user_id=user.user_id, name=user.name, goal=user.goal,
                        intensity=user.intensity, workout_plan=revised,
                        nutrition_tip=plan.nutrition_tip, updated=True)

@router.get("/api/users", response_model=list[UserSummary])
def api_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    plans = {p.user_id: p for p in db.scalars(select(Plan)).all()}
    return [row(u, plans.get(u.user_id)) for u in users]

@router.delete("/api/users/{user_id}")
def api_delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.user_id == user_id))
    plan = db.scalar(select(Plan).where(Plan.user_id == user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if plan: db.delete(plan)
    db.delete(user)
    db.commit()
    return {"message": "User deleted", "user_id": user_id}
