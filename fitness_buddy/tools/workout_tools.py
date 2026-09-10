"""
Workout generation tools using IBM Granite via watsonx.ai
"""
import os
import requests
from typing import Optional
from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission

WATSONX_URL = os.environ.get(
    "IBM_WATSONX_URL",
    "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29",
)
MODEL_ID  = os.environ.get("IBM_MODEL_ID",   "ibm/granite-4-h-small")
PROJECT_ID = os.environ.get("IBM_PROJECT_ID", "")
API_KEY    = os.environ.get("IBM_API_KEY",    "")


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


def _generate(prompt: str, max_tokens: int = 600) -> str:
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


class WorkoutInput(BaseModel):
    fitness_level: str = Field(description="Beginner, Intermediate, or Advanced")
    goal: str = Field(description="e.g. weight loss, muscle gain, endurance, flexibility")
    duration_minutes: int = Field(default=30, description="Workout duration in minutes")
    equipment: Optional[str] = Field(default="none", description="Available equipment, e.g. dumbbells, gym, none")


class WorkoutOutput(BaseModel):
    workout_plan: str = Field(description="Personalized workout plan")
    safety_tips: str = Field(description="Safety and form tips")


@tool(permission=ToolPermission.READ_ONLY)
def generate_workout_plan(input: WorkoutInput) -> WorkoutOutput:
    """
    Generate a personalized workout plan using IBM Granite.

    Args:
        input (WorkoutInput): Fitness level, goal, duration, and equipment details.

    Returns:
        WorkoutOutput: A structured workout plan with safety tips.
    """
    prompt = (
        f"You are a certified personal trainer. Create a safe, effective {input.duration_minutes}-minute "
        f"workout plan for a {input.fitness_level} level person whose goal is {input.goal}. "
        f"Available equipment: {input.equipment}. "
        "Include warm-up, main exercises (sets, reps, rest), and cool-down. "
        "Then provide 3 key safety and form tips. "
        "Format clearly with sections: WARM-UP, MAIN WORKOUT, COOL-DOWN, SAFETY TIPS."
    )
    text = _generate(prompt, max_tokens=700)
    # Split safety tips from plan
    if "SAFETY TIPS" in text.upper():
        parts = text.upper().split("SAFETY TIPS")
        plan = text[: len(text) - len(parts[-1]) - len("SAFETY TIPS")]
        tips = "SAFETY TIPS" + parts[-1]
    else:
        plan = text
        tips = "Always listen to your body, stay hydrated, and stop if you feel pain."
    return WorkoutOutput(workout_plan=plan.strip(), safety_tips=tips.strip())
