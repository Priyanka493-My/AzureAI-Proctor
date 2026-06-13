import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
from backend.app.local_rag import LocalSyllabusRAG
from backend.app.llm_judge import LLMJudge

class ProctorOrchestrator:
    def __init__(self):
        print("Initializing complete AI Proctor Core System...")

        # 1. Spin up the vector database engine
        self.rag_engine = LocalSyllabusRAG()
        self.rag_engine.initialize_vector_store()

        # 2. Spin up the evaluation brain
        self.judge_engine = LLMJudge()
        print("Core systems online and synchronized!\n")

    def run_proctor(self,question: str, user_answer: str)->str:
        """
        Coordinates the end-to-end flow: searches the vector store for context,
        then feeds that context and the user's answer into the LLM Judge.
        """
        print(f" Step 1: Scanning vector index for question boundaries...")
        # Automatically fetch the top 2 matching context blocks from the PDF
        retrieved_context = self.rag_engine.retrieve_context(question,top_k = 2)

        print(f" Step 2: Shipping context to Llama-3.1 via Groq for evaluation...")
        # Pass everything to the judge

        evaluation_report = self.judge_engine.evaluate_answer(question=question,
            user_answer=user_answer,
            retrieved_context=retrieved_context)

        return evaluation_report

if __name__ == "__main__":
    orchestrator = ProctorOrchestrator()

    # Example Scenario: Testing Microsoft Foundry Tools (Domain 2)
    sample_question = "Explain how to extract data schemas from complex files in Microsoft Foundry."

    # A solid student response that matches our mock syllabus rules perfectly
    good_student_answer = (
        "We can extract structured data schemas from complex forms, text, images, audio, "
        "and video files using Azure Content Understanding features inside Microsoft Foundry."
    )

    print("-" * 60)
    print(f"📝 SIMULATED QUESTION: {sample_question}")
    print(f"👤 STUDENT ANSWER: {good_student_answer}")
    print("-" * 60)

    # Run the full pipeline!
    final_report = orchestrator.run_proctor(sample_question, good_student_answer)

    print("\n📊 [FINAL EVALUATION REPORT FROM PROCTOR]:")
    print(final_report)
