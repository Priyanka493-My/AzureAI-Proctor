import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_syllabus():
    # Targets the root directory where local_rag.py looks for it
    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "ai900_syllabus.pdf"))
    print(f"🛠️ Generating dummy syllabus at: {pdf_path}")

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Clean heading formatting
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12
    )

    # Realistically structured text mapping the new 2026 AI-901 core blueprint
    syllabus_content = [
        ("EXAM AI-901: MICROSOFT AZURE AI FUNDAMENTALS (2026 BLUEPRINT)",
         "Validates introductory knowledge of foundational AI concepts and practical application deployment using Microsoft Foundry."),

        ("DOMAIN 1: IDENTIFY AI CONCEPTS AND RESPONSIBILITIES (40-45%)",
         "Evaluate real-world applications against the six core Responsible AI Principles: "
         "Fairness, Reliability and Safety, Privacy and Security, Inclusiveness, Transparency, and Accountability. "
         "Understand how generative AI models function, select appropriate foundation models based on client capabilities, "
         "and configure key deployment parameters like model temperature, latency rules, and inference constraints."),

        ("DOMAIN 2: IMPLEMENT AI SOLUTIONS BY USING MICROSOFT FOUNDRY (55-60%)",
         "Understand how to use modern Microsoft Foundry projects and tools to build, deploy, and monitor interactive AI applications and autonomous agents. "
         "Implement text analytics solutions including sentiment analysis and keyword extraction. "
         "Deploy text-to-speech and speech-to-text workflows using Azure Speech tools in Foundry. "
         "Process computer vision and multimodal inputs using deployed foundational models, and utilize Azure Content Understanding "
         "features to extract structured data schemas from complex forms, text, images, audio, and video files."),

        ("TECHNICAL REQUIREMENTS & PYTHON SDK",
         "Candidates must demonstrate basic technical implementation capacity, including familiarity with using "
         "the unified Python SDK, CLI interfaces, and REST API structures required to connect to a deployed model, "
         "manage message structures for Foundry projects, and write light client scripts for agentic applications.")
    ]

    for title, body in syllabus_content:
        story.append(Paragraph(title, heading_style))
        story.append(Paragraph(body, styles['BodyText']))
        story.append(Spacer(1, 15))

    doc.build(story)
    print("✅ AI-901 Mock Syllabus PDF created successfully!")


if __name__ == "__main__":
    generate_syllabus()