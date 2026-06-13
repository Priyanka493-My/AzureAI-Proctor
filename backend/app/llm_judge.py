import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class LLMJudge:
    def __init__(self):
        # Fetch the API key from the environment
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Missing GROQ_API_KEY in environment or .env file!")

        # Initialize the official Groq client
        self.client = Groq(api_key = self.api_key)

        self.model_name = "llama-3.1-8b-instant"

    def evaluate_answer(self,question:str,user_answer:str,retrieved_context : str)->str:
        """
        Acts as an Agentic Interviewer using the Foundry IQ grounding layer to evaluate
        an AI-901 Beta exam response, enforcing gamified grading metrics.
        """
        # Crafting a strict system prompt to control the LLM's behavioral persona
        system_instruction = (
            "You are an expert AI-901 Azure AI Fundamentals Technical Interviewer and Proctor.\n"
            "Your task is to judge the student's answer based strictly on the provided Microsoft Foundry syllabus context.\n\n"
            
            "CRITICAL FORMATTING RULE:\n"
            "Your response MUST start with one of these three exact tags on the very first line:\n"
            "- 'SCORE: Pass' (The answer is technically accurate and directly addresses the core question metrics)\n"
            "- 'SCORE: Partial' (The answer is partially accurate or suffers from a Cross-Domain mix-up, but shows relevant technical knowledge)\n"
            "- 'SCORE: Fail' (The answer is completely incorrect, blank, or factually irrelevant to the question asked)\n\n"
            
            "Following the score line, provide your breakdown using this exact structure:\n"
            "REASONING: [1-2 sentences explaining exactly why you assigned that score, calling out specific Foundry concepts or Domain mismatches]\n"
            "FEEDBACK: [1 high-impact, actionable study hint or specify Python SDK/Foundry tools they missed to help them pass the AI-901 exam]\n\n"
            "Stay strictly grounded in the provided syllabus text. Do not invent features outside the context."
        )
        # Setting up the prompt structure with clear boundaries
        user_prompt = f"""
        ======================
        FOUNDRY IQ CONTEXT:
        {retrieved_context}
        ======================
        INTERVIEW QUESTION: {question}
        ======================
        STUDENT ANSWER: {user_answer}
        ======================
        Provide your evaluation report following the strict formatting layout guidelines:
        """
        try:
            response = self.client.chat.completions.create(
                model = self.model_name,
                messages = [{"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_prompt}],
                temperature=0.1,  # Low temperature makes the grading deterministic and strict
                max_tokens=250
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"SCORE: Fail\nREASONING: The agent encountered an unexpected API error during processing.\nFEEDBACK: Check your local network or API key settings. Error details: {str(e)}"


if __name__ == "__main__":
    # Quick localized sanity check to verify your API connection works!
    print("🚀 Initializing local LLM Judge test...")
    judge = LLMJudge()

    # Mock data to test the wire connection
    mock_q = "What are the core pillars of Domain 1?"
    mock_context = "DOMAIN 1 covers six core Responsible AI Principles: Fairness, Reliability, and Safety."
    mock_answer = "Domain 1 is all about building fast models and writing SQL algorithms."

    print("🧠 Querying Groq API for grading...")
    result = judge.evaluate_answer(mock_q, mock_answer, mock_context)

    print("\n🏁 [JUDGE RESPONSE]:")
    print(result)