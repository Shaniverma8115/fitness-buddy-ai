"""
Nutrition guidance tools using IBM Granite via watsonx.ai
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


class NutritionInput(BaseModel):
    goal: str = Field(description="Nutrition goal: weight loss, muscle gain, maintenance, energy boost")
    dietary_restrictions: Optional[str] = Field(default="none", description="e.g. vegan, gluten-free, lactose intolerant, none")
    age: Optional[int] = Field(default=30, description="User age in years")
    activity_level: Optional[str] = Field(default="moderate", description="sedentary, light, moderate, active, very active")


class NutritionOutput(BaseModel):
    daily_calorie_target: str = Field(description="Recommended daily calorie intake")
    macros_breakdown: str = Field(description="Protein, carbs, and fat breakdown")
    nutrition_tips: str = Field(description="Practical daily nutrition tips")


@tool(permission=ToolPermission.READ_ONLY)
def get_nutrition_guidance(input: NutritionInput) -> NutritionOutput:
    """
    Provide personalized daily nutrition guidance using IBM Granite.

    Args:
        input (NutritionInput): Goal, dietary restrictions, age, and activity level.

    Returns:
        NutritionOutput: Calorie target, macros breakdown, and daily nutrition tips.
    """
    prompt = (
        f"You are a registered dietitian. Provide personalized nutrition guidance for a "
        f"{input.age}-year-old with {input.activity_level} activity level whose goal is {input.goal}. "
        f"Dietary restrictions: {input.dietary_restrictions}. "
        "Give: 1) Daily calorie target with reasoning. "
        "2) Macros breakdown (protein g, carbs g, fat g). "
        "3) Five practical daily nutrition tips. "
        "Format with sections: CALORIE TARGET, MACROS BREAKDOWN, DAILY TIPS."
    )
    text = _generate(prompt, max_tokens=600)

    calorie = ""
    macros = ""
    tips = ""

    text_upper = text.upper()
    if "CALORIE TARGET" in text_upper:
        start = text_upper.index("CALORIE TARGET")
        end = text_upper.index("MACROS BREAKDOWN") if "MACROS BREAKDOWN" in text_upper else len(text)
        calorie = text[start:end].strip()
    if "MACROS BREAKDOWN" in text_upper:
        start = text_upper.index("MACROS BREAKDOWN")
        end = text_upper.index("DAILY TIPS") if "DAILY TIPS" in text_upper else len(text)
        macros = text[start:end].strip()
    if "DAILY TIPS" in text_upper:
        start = text_upper.index("DAILY TIPS")
        tips = text[start:].strip()

    if not calorie:
        calorie = text[:200]
    if not macros:
        macros = "Balanced macros based on your goal."
    if not tips:
        tips = text[-300:] if len(text) > 300 else text

    return NutritionOutput(
        daily_calorie_target=calorie,
        macros_breakdown=macros,
        nutrition_tips=tips,
    )


class MealPlanInput(BaseModel):
    goal: str = Field(description="Meal goal: weight loss, muscle gain, maintenance, energy")
    dietary_restrictions: Optional[str] = Field(default="none", description="Dietary preferences or restrictions")
    meals_per_day: Optional[int] = Field(default=3, description="Number of meals per day (2-6)")


class MealPlanOutput(BaseModel):
    meal_plan: str = Field(description="Full day healthy meal plan with recipes/ideas")


@tool(permission=ToolPermission.READ_ONLY)
def generate_healthy_meal_plan(input: MealPlanInput) -> MealPlanOutput:
    """
    Generate a full-day healthy meal plan using IBM Granite.

    Args:
        input (MealPlanInput): Goal, dietary restrictions, and meals per day.

    Returns:
        MealPlanOutput: A structured healthy meal plan for the day.
    """
    prompt = (
        f"You are a nutritionist chef. Create a healthy, delicious {input.meals_per_day}-meal-per-day plan "
        f"for someone whose goal is {input.goal}. "
        f"Dietary restrictions: {input.dietary_restrictions}. "
        "For each meal include: meal name, key ingredients, brief preparation note, and approximate calories. "
        "Also suggest 1-2 healthy snack options. Keep it practical and affordable."
    )
    text = _generate(prompt, max_tokens=700)
    return MealPlanOutput(meal_plan=text)
