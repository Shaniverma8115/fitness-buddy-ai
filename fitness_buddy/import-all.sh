#!/usr/bin/env bash
# Fitness Buddy — Import all tools and agent into watsonx Orchestrate
# Usage: bash import-all.sh

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "======================================================"
echo "  Fitness Buddy — watsonx Orchestrate Import Script  "
echo "======================================================"

# ── Import Python tools ───────────────────────────────────
echo ""
echo "[1/3] Importing Python tools..."

for tool in workout_tools.py nutrition_tools.py lifestyle_tools.py; do
  echo "  Importing tool: ${tool}"
  orchestrate tools import -k python -f "${SCRIPT_DIR}/tools/${tool}"
done

# ── Import Agent ──────────────────────────────────────────
echo ""
echo "[2/3] Importing agent..."

for agent in fitness_buddy.yaml; do
  echo "  Importing agent: ${agent}"
  orchestrate agents import -f "${SCRIPT_DIR}/agents/${agent}"
done

echo ""
echo "[3/3] Done! ✅"
echo ""
echo "To chat with Fitness Buddy:"
echo "  orchestrate chat start"
echo "Then select 'fitness_buddy' from the agent list."
echo "======================================================"
