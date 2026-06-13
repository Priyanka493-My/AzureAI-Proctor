import streamlit as str_ui
import requests
import json
import random
import os

# Set up the web page title and visual layout configuration
str_ui.set_page_config(
    page_title="AzureAI-Proctor Agent Arena",
    page_icon="⚔️",
    layout="centered"
)

# 1. Initialize persistent Game State tracking variables across page refreshes
if "total_score" not in str_ui.session_state:
    str_ui.session_state["total_score"] = 0
if "history_log" not in str_ui.session_state:
    str_ui.session_state["history_log"] = []
if "current_question" not in str_ui.session_state:
    str_ui.session_state["current_question"] = ""
if "last_domain" not in str_ui.session_state:
    str_ui.session_state["last_domain"] = ""

# 2. Load the Blueprint Question Bank safely from file
json_path = os.path.join(os.path.dirname(__file__), "questions.json")
try:
    with open(json_path, "r") as f:
        question_bank = json.load(f)
except Exception as e:
    str_ui.error(f"⚠️ Error loading questions.json: {e}")
    # Fallback to prevent app crash if json file isn't present yet
    question_bank = {
        "Domain 2: Implement AI Solutions by using Microsoft Foundry (55-60%)": [
            "Explain how to extract data schemas from complex files in Microsoft Foundry."
        ]
    }

# Application Header UI
str_ui.title("⚔️ AzureAI-Proctor: Reasoning Agent Arena")
str_ui.markdown("### Track: Reasoning Agents | Intel Layer: Foundry IQ")

# Gamified Leaderboard Metrics Display Panel
score_col, target_col = str_ui.columns(2)
with score_col:
    str_ui.metric(label="🏆 Your Score Profile", value=f"{str_ui.session_state['total_score']} XP")
with target_col:
    str_ui.metric(label="🎯 Active Exam Target", value="AI-901 Beta")

str_ui.write("---")

# Objective Domain Selection Dropdown Component
selected_domain = str_ui.selectbox(
    "🎯 Select the AI-901 Objective Domain you want to practice:",
    options=list(question_bank.keys())
)

# Handle random initialization or change of target domain boundary
if not str_ui.session_state["current_question"] or str_ui.session_state["last_domain"] != selected_domain:
    str_ui.session_state["current_question"] = random.choice(question_bank[selected_domain])
    str_ui.session_state["last_domain"] = selected_domain

# Manual Question Shuffling Tool
if str_ui.button("🔄 Cycle to New Question"):
    str_ui.session_state["current_question"] = random.choice(question_bank[selected_domain])
    str_ui.rerun()

# Present the Active Interview Target Question
str_ui.subheader("🗣️ The Technical Interviewer Asks:")
str_ui.info(str_ui.session_state["current_question"])

# Input capture text workspace
user_input = str_ui.text_area(
    label="Type your active-recall response below:",
    placeholder="Provide technical depth. Mention specific Azure tools or Responsible AI parameters...",
    height=150
)

# Core Submission Assessment Loop
if str_ui.button("Submit Response to Proctor", type="primary"):
    if not user_input.strip():
        str_ui.warning("⚠️ Please type an answer before submitting to the Reasoning Agent!")
    else:
        with str_ui.spinner("🤖 Agent is scanning Foundry IQ knowledge and checking your answer..."):
            try:
                backend_url = "http://127.0.0.1:8000/api/evaluate"
                data_payload = {
                    "question": str_ui.session_state["current_question"],
                    "user_answer": user_input
                }

                # Post request transit down the FastAPI channel
                response = requests.post(backend_url, json=data_payload)

                if response.status_code == 200:
                    api_result = response.json()

                    # Programmatic extraction of our backend parsed data fields
                    score_received = api_result.get("score", "Fail")
                    raw_report = api_result.get("evaluation_report", "")

                    # Map categorical scoring outputs into gamified metric numbers
                    points_awarded = 0
                    if score_received == "Pass":
                        points_awarded = 100
                    elif score_received == "Partial":
                        points_awarded = 50

                    # Append to tracking arrays and session histories
                    str_ui.session_state["total_score"] += points_awarded
                    str_ui.session_state["history_log"].append({
                        "question": str_ui.session_state["current_question"],
                        "domain": selected_domain,
                        "score": score_received,
                        "xp": points_awarded
                    })

                    # Show Results UI Box elements
                    str_ui.success("📊 Proctor Evaluation Processed!")

                    if points_awarded > 0:
                        str_ui.balloons()
                        str_ui.toast(f"🎉 Earned +{points_awarded} XP!", icon="⭐")

                    str_ui.write(f"### 🏁 Evaluation Outcome: **{score_received}** (+{points_awarded} XP)")
                    str_ui.markdown(f"```text\n{raw_report}\n```")

                    # Soft instruction reminding the user they can move to another test metric
                    str_ui.write("💡 Click **'Cycle to New Question'** above to generate your next technical challenge!")
                else:
                    str_ui.error(f"❌ Backend returned an error code: {response.status_code}")

            except requests.exceptions.ConnectionError:
                str_ui.error(
                    "❌ Connection Failed! Make sure your FastAPI server is running in your first terminal tab.")

# Session History Progress panel container component
if str_ui.session_state["history_log"]:
    str_ui.write("---")
    with str_ui.expander("📋 View active interview session progress analytics"):
        for i, log in enumerate(reversed(str_ui.session_state["history_log"])):
            status_emoji = "✅" if log["score"] == "Pass" else "⚠️" if log["score"] == "Partial" else "❌"
            str_ui.write(f"**Attempt {len(str_ui.session_state['history_log'])-i}:** {status_emoji} | **{log['score']}** ({log['xp']} XP) — *{log['question']}*")