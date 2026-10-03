# =====================================================
# ASK GEMINI
# =====================================================

def ask_gemini(question, context):

    client = get_gemini_client()

    if client is None:

        return """
⚠️ Gemini API is not connected.

Please check:

Streamlit Cloud → Settings → Secrets

Make sure GEMINI_API_KEY is added.
"""

    system_prompt = """
You are Study with Subha, an AI study assistant.

Your job is to help students understand their study materials.

Rules:

1. Give simple and clear answers.
2. If the user asks in Bengali, answer in Bengali.
3. If the user asks in English, answer in simple English.
4. For exams, provide easy exam-ready answers.
5. Use the provided study material when relevant.
6. Do not invent information that is not supported by the material.
7. If the answer is not available in the material, clearly say that.
8. Use headings and bullet points when useful.
9. Keep explanations suitable for a college student.
"""

    user_prompt = f"""
{system_prompt}

STUDY MATERIAL:

{context}

STUDENT QUESTION:

{question}

Answer the student's question clearly.
"""

    # Models to try
    models_to_try = [
        "gemini-3.8-flash",
        "gemini-3.8-flash-lite"
    ]

    last_error = None

    for model_name in models_to_try:

        # Try each model up to 2 times
        for attempt in range(2):

            try:

                response = client.models.generate_content(
                    model=model_name,
                    contents=user_prompt
                )

                if response and response.text:

                    return response.text

            except Exception as e:

                last_error = e

                error_text = str(e)

                # Temporary Gemini server problem
                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                ):

                    import time

                    time.sleep(2)

                    continue

                # Other errors
                return f"""
⚠️ Gemini API error.

Error:

{e}
"""

    return f"""
⚠️ Gemini is temporarily unavailable.

I tried the available models several times,
but Google's server returned 503 UNAVAILABLE.

Please try again after some time.

Last error:

{last_error}