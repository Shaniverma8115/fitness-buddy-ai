# Fitness Buddy 💪

**Your Personalized AI Wellness Coach — Powered by IBM Granite on watsonx.ai**

Fitness Buddy is a fully featured AI agent built with **IBM watsonx Orchestrate** and **IBM Granite 4H Small**. It delivers personalized workouts, nutrition guidance, healthy meal plans, motivational support, habit-building programs, and safe lifestyle recommendations — all in real time.

---

## Architecture Diagram

```mermaid
graph TB
    User["👤 User<br/>(Web Chat UI)"] -->|Message| FE["🌐 Frontend<br/>fitness_buddy/frontend/index.html"]
    FE -->|Direct API call<br/>IBM Granite| WX["☁️ watsonx.ai<br/>ibm/granite-4-h-small<br/>us-south"]
    
    User2["👤 User<br/>(Orchestrate UI)"] -->|Chat| Agent["🤖 Fitness Buddy Agent<br/>fitness_buddy"]
    Agent -->|Invokes| T1["🏋️ generate_workout_plan"]
    Agent -->|Invokes| T2["🥗 get_nutrition_guidance"]
    Agent -->|Invokes| T3["🍽️ generate_healthy_meal_plan"]
    Agent -->|Invokes| T4["⚡ get_motivation_boost"]
    Agent -->|Invokes| T5["📅 build_healthy_habit_plan"]
    Agent -->|Invokes| T6["🌿 get_lifestyle_recommendations"]
    
    T1 & T2 & T3 & T4 & T5 & T6 -->|IBM Granite API| WX
    
    style User fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style User2 fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style FE fill:#7C3AED,stroke:#5B21B6,color:#fff
    style Agent fill:#6366F1,stroke:#4338CA,color:#fff
    style WX fill:#0EA5E9,stroke:#0284C7,color:#fff
    style T1 fill:#F59E0B,stroke:#D97706,color:#fff
    style T2 fill:#10B981,stroke:#059669,color:#fff
    style T3 fill:#EF4444,stroke:#DC2626,color:#fff
    style T4 fill:#F97316,stroke:#EA580C,color:#fff
    style T5 fill:#8B5CF6,stroke:#7C3AED,color:#fff
    style T6 fill:#14B8A6,stroke:#0D9488,color:#fff
```

---

## Agent Flow Diagram

```mermaid
flowchart TD
    Start(["🚀 User Message"]) --> Classify{{"🤖 Fitness Buddy<br/>IBM Granite LLM<br/>Understands Intent"}}

    Classify -->|"Workout request"| W["🏋️ generate_workout_plan<br/>(workout_tools.py)"]
    Classify -->|"Nutrition question"| N["🥗 get_nutrition_guidance<br/>(nutrition_tools.py)"]
    Classify -->|"Meal plan request"| M["🍽️ generate_healthy_meal_plan<br/>(nutrition_tools.py)"]
    Classify -->|"Feeling demotivated"| MO["⚡ get_motivation_boost<br/>(lifestyle_tools.py)"]
    Classify -->|"Build a habit"| H["📅 build_healthy_habit_plan<br/>(lifestyle_tools.py)"]
    Classify -->|"Lifestyle concern"| L["🌿 get_lifestyle_recommendations<br/>(lifestyle_tools.py)"]

    W & N & M & MO & H & L --> Granite{{"☁️ IBM Granite 4H Small<br/>watsonx.ai API"}}
    Granite --> Response["📝 Structured Response<br/>(plan / tips / schedule)"]
    Response --> Format["🤖 Agent Formats &<br/>Presents to User"]
    Format --> End(["✅ User Gets<br/>Personalized Guidance"])

    style Start fill:#2ECC71,stroke:#27AE60,color:#fff
    style End fill:#2ECC71,stroke:#27AE60,color:#fff
    style Classify fill:#6366F1,stroke:#4338CA,color:#fff
    style Granite fill:#0EA5E9,stroke:#0284C7,color:#fff
    style Response fill:#F59E0B,stroke:#D97706,color:#fff
    style Format fill:#6366F1,stroke:#4338CA,color:#fff
    style W fill:#F59E0B,stroke:#D97706,color:#fff
    style N fill:#10B981,stroke:#059669,color:#fff
    style M fill:#EF4444,stroke:#DC2626,color:#fff
    style MO fill:#F97316,stroke:#EA580C,color:#fff
    style H fill:#8B5CF6,stroke:#7C3AED,color:#fff
    style L fill:#14B8A6,stroke:#0D9488,color:#fff
```

---

## Project Structure

```
fitness_buddy/
├── __init__.py
├── README.md
├── import-all.sh               # CLI import script
├── agents/
│   └── fitness_buddy.yaml      # Agent configuration (watsonx Orchestrate)
├── tools/
│   ├── __init__.py
│   ├── workout_tools.py        # generate_workout_plan tool
│   ├── nutrition_tools.py      # get_nutrition_guidance + generate_healthy_meal_plan
│   └── lifestyle_tools.py      # get_motivation_boost + build_healthy_habit_plan + get_lifestyle_recommendations
├── frontend/
│   └── index.html              # Standalone web chat UI (IBM Granite direct integration)
└── generated/                  # Generated flow specs (if any)
```

---

## Tools Reference

| Tool | File | Description |
|------|------|-------------|
| `generate_workout_plan` | `workout_tools.py` | Personalized workout plan (warm-up, main, cool-down, safety tips) |
| `get_nutrition_guidance` | `nutrition_tools.py` | Daily calorie target, macros breakdown, nutrition tips |
| `generate_healthy_meal_plan` | `nutrition_tools.py` | Full-day meal plan with ingredients & calories |
| `get_motivation_boost` | `lifestyle_tools.py` | Motivational message + 3 concrete action steps |
| `build_healthy_habit_plan` | `lifestyle_tools.py` | Week-by-week habit plan + science-backed hacks |
| `get_lifestyle_recommendations` | `lifestyle_tools.py` | Holistic lifestyle advice + sample daily schedule |

---

## IBM Granite Configuration

| Parameter | Value |
|-----------|-------|
| API Endpoint | `https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29` |
| Model ID | `ibm/granite-4-h-small` |
| Project ID | `76edf6b0-8919-446e-93dc-43e0b6a7e481` |
| Decoding | Greedy |
| Max New Tokens | 600–800 |

---

## Usage

### Option 1: Web Chat UI (Standalone Frontend)

Open `frontend/index.html` directly in any modern browser. The page communicates directly with IBM Granite on watsonx.ai via your API key — no backend server needed.

```bash
# Windows
start fitness_buddy/frontend/index.html

# macOS
open fitness_buddy/frontend/index.html

# Linux
xdg-open fitness_buddy/frontend/index.html
```

Features:
- 🎨 Dark-themed chat UI with quick-action sidebar
- 💬 Multi-turn conversation with context memory
- ⚡ Direct IBM Granite integration
- 📱 Mobile responsive

### Option 2: watsonx Orchestrate Agent

```bash
# 1. Import all tools and agent
bash fitness_buddy/import-all.sh

# 2. Start the chat
orchestrate chat start
# Select 'fitness_buddy' from the agent list
```

---

## Capabilities

### 🏋️ Personalized Workouts
- Tailored to fitness level: Beginner / Intermediate / Advanced
- Goals: weight loss, muscle gain, endurance, flexibility
- Equipment-aware: bodyweight, dumbbells, full gym
- Structured with warm-up → main → cool-down + safety tips

### 🥗 Nutrition Guidance
- Daily calorie targets based on age, activity level & goal
- Macro breakdowns (protein / carbs / fat in grams)
- Practical daily nutrition tips for sustainable results

### 🍽️ Healthy Meal Plans
- Full-day plans (2–6 meals) with ingredients & calorie estimates
- Goal-aligned: weight loss, muscle gain, maintenance, energy
- Dietary restriction aware: vegan, gluten-free, lactose-free, etc.

### ⚡ Motivation & Accountability
- Empathetic, personalized motivational messages
- Concrete same-day action steps to overcome blocks
- Science-backed strategies for consistency

### 📅 Habit Building
- Week-by-week progressive habit plans
- Habit stacking, cue-routine-reward framework
- Customizable timeframe (1–12 weeks)

### 🌿 Lifestyle Recommendations
- Sleep hygiene, stress management, energy optimization
- Movement breaks for sedentary workers
- Sample healthy daily schedule tailored to occupation

---

## Safety Disclaimer

> Fitness Buddy provides general wellness information for educational purposes. Always consult a qualified healthcare professional, physician, or registered dietitian before starting any new exercise program, diet, or making significant lifestyle changes — especially if you have existing health conditions.
