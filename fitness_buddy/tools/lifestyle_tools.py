"""
Motivation, habit-building, and lifestyle tools using IBM Granite via watsonx.ai
"""
import requests
from typing import Optional
from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission

WATSONX_URL = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
MODEL_ID = "ibm/granite-4-h-small"
PROJECT_ID = "76edf6b0-8919-446e-93dc-43e0b6a7e481"
API_KEY = "0WeqfqiHKVKp-CFVrBD2NKSL49yJ99OvFxp85sPf9IRB"


def _get_iam_token() -> str:
    """Exchange IBM API key for IAM bearer token."""
    resp = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={API_KEY}",
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _generate(prompt: str, max_tokens: int = 500) -> str:
    """Call IBM Granite to generate text."""
    token = _get_iam_token()
    payload = {
        "model_id": MODEL_ID,
        "project_id": PROJECT_ID,
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": max_tokens,
            "repetition_penalty": 1.1,
        },
    }
    resp = requests.post(
        WATSONX_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0].get("generated_text", "").strip() if results else ""


# ─── Motivation ───────────────────────────────────────────────────────────────

class MotivationInput(BaseModel):
    struggle: str = Field(description="What the user is struggling with, e.g. skipping workouts, low energy, plateau")
    fitness_goal: Optional[str] = Field(default="", description="The user's fitness goal")


class MotivationOutput(BaseModel):
    motivational_message: str = Field(description="Personalized motivational message")
    action_steps: str = Field(description="3 concrete action steps to get back on track")


@tool(permission=ToolPermission.READ_ONLY)
def get_motivation_boost(input: MotivationInput) -> MotivationOutput:
    """
    Deliver a personalized motivational message and concrete action steps using IBM Granite.

    Args:
        input (MotivationInput): The user's struggle and fitness goal.

    Returns:
        MotivationOutput: An uplifting message and 3 concrete action steps.
    """
    prompt = (
        f"You are an empathetic fitness coach and motivational speaker. "
        f"A user is struggling with: {input.struggle}. "
        f"Their goal is: {input.fitness_goal or 'improving their health'}. "
        "Write: 1) A powerful, warm, and personalized motivational message (3-4 sentences). "
        "2) Three specific, actionable steps they can take TODAY to get back on track. "
        "Be encouraging, realistic, and science-backed. "
        "Sections: MOTIVATIONAL MESSAGE, ACTION STEPS."
    )
    text = _generate(prompt, max_tokens=500)

    msg = text
    steps = ""
    text_upper = text.upper()
    if "MOTIVATIONAL MESSAGE" in text_upper:
        start = text_upper.index("MOTIVATIONAL MESSAGE")
        end = text_upper.index("ACTION STEPS") if "ACTION STEPS" in text_upper else len(text)
        msg = text[start:end].strip()
    if "ACTION STEPS" in text_upper:
        start = text_upper.index("ACTION STEPS")
        steps = text[start:].strip()

    return MotivationOutput(motivational_message=msg, action_steps=steps)


# ─── Habit Building ────────────────────────────────────────────────────────────

class HabitInput(BaseModel):
    desired_habit: str = Field(description="The healthy habit the user wants to build, e.g. morning exercise, drinking more water")
    current_routine: Optional[str] = Field(default="no established routine", description="Brief description of current daily routine")
    timeframe_weeks: Optional[int] = Field(default=4, description="Weeks to build the habit (1-12)")


class HabitOutput(BaseModel):
    habit_plan: str = Field(description="Week-by-week habit-building plan")
    habit_hacks: str = Field(description="Science-backed habit hacks and tips")


@tool(permission=ToolPermission.READ_ONLY)
def build_healthy_habit_plan(input: HabitInput) -> HabitOutput:
    """
    Create a science-backed habit-building plan using IBM Granite.

    Args:
        input (HabitInput): Desired habit, current routine, and timeframe.

    Returns:
        HabitOutput: A structured habit plan with science-backed hacks.
    """
    prompt = (
        f"You are a behavioral psychologist and health coach. "
        f"Help a user build the habit: '{input.desired_habit}' over {input.timeframe_weeks} weeks. "
        f"Their current routine: {input.current_routine}. "
        "Provide: 1) A week-by-week progressive habit plan (mini milestones). "
        "2) Five science-backed habit hacks (habit stacking, cue-routine-reward loop, etc.). "
        "Keep it practical and encouraging. "
        "Sections: HABIT PLAN, HABIT HACKS."
    )
    text = _generate(prompt, max_tokens=600)

    plan = text
    hacks = ""
    text_upper = text.upper()
    if "HABIT PLAN" in text_upper:
        start = text_upper.index("HABIT PLAN")
        end = text_upper.index("HABIT HACKS") if "HABIT HACKS" in text_upper else len(text)
        plan = text[start:end].strip()
    if "HABIT HACKS" in text_upper:
        start = text_upper.index("HABIT HACKS")
        hacks = text[start:].strip()

    return HabitOutput(habit_plan=plan, habit_hacks=hacks)


# ─── Lifestyle Recommendations ─────────────────────────────────────────────────

class LifestyleInput(BaseModel):
    concern: str = Field(description="User's lifestyle concern, e.g. poor sleep, high stress, sedentary job, low energy")
    age: Optional[int] = Field(default=30, description="User's age")
    occupation: Optional[str] = Field(default="office worker", description="User's occupation")


class LifestyleOutput(BaseModel):
    lifestyle_advice: str = Field(description="Safe, holistic lifestyle recommendations")
    daily_schedule: str = Field(description="Sample healthy daily schedule")


@tool(permission=ToolPermission.READ_ONLY)
def get_lifestyle_recommendations(input: LifestyleInput) -> LifestyleOutput:
    """
    Provide safe, holistic lifestyle recommendations using IBM Granite.

    Args:
        input (LifestyleInput): User's concern, age, and occupation.

    Returns:
        LifestyleOutput: Holistic lifestyle advice and a sample daily schedule.
    """
    prompt = (
        f"You are a holistic wellness expert and lifestyle coach. "
        f"A {input.age}-year-old {input.occupation} has this concern: {input.concern}. "
        "Provide: 1) Safe, evidence-based lifestyle recommendations addressing their concern (5 tips). "
        "2) A sample healthy daily schedule (morning to evening) tailored to their situation. "
        "Include sleep hygiene, stress management, movement breaks, and mental wellness tips. "
        "Sections: LIFESTYLE ADVICE, DAILY SCHEDULE."
    )
    text = _generate(prompt, max_tokens=700)

    advice = text
    schedule = ""
    text_upper = text.upper()
    if "LIFESTYLE ADVICE" in text_upper:
        start = text_upper.index("LIFESTYLE ADVICE")
        end = text_upper.index("DAILY SCHEDULE") if "DAILY SCHEDULE" in text_upper else len(text)
        advice = text[start:end].strip()
    if "DAILY SCHEDULE" in text_upper:
        start = text_upper.index("DAILY SCHEDULE")
        schedule = text[start:].strip()

    return LifestyleOutput(lifestyle_advice=advice, daily_schedule=schedule)
