import ollama
import re
import json

def extract_json_block(text: str) -> dict:
    """
    Extracts a JSON block from LLM output using regex.
    """
    # Try to find JSON inside triple backticks ```json ... ```
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not match:
        # Fallback: try to match just any JSON object {...}
        match = re.search(r"(\{.*?\})", text, re.DOTALL)

    if match:
        json_text = match.group(1)
        return json.loads(json_text)
    else:
        raise ValueError("No valid JSON object found.")

def generate_answer_and_update_result(job: dict, job_id: str):
    job_data = job[job_id]
    result = job_data["result"]

    transcription = result.get("transcription", "")
    prompt_fields = {k: v for k, v in result.items() if k != "transcription"}

    prompts_text = ""
    for key, prompt in prompt_fields.items():
        prompts_text += f"\n- {key}: {prompt}"

    full_prompt = f"""
You are a helpful assistant. Based on the transcription provided, answer the following prompts.

Transcription:
\"\"\"
{transcription}
\"\"\"

Prompts:{prompts_text}

Return your answer strictly in JSON format like:
{{
  "summary": "...",
  "keyword": "..."
}}

Only include the JSON. No explanation. No markdown. No extra text.
"""

    try:
        response = ollama.chat(
            model="deepseek-r1:1.5b",
            messages=[{"role": "user", "content": full_prompt}]
        )
        raw_output = response["message"]["content"].strip()
        print("🔍 Raw LLM Output:", repr(raw_output))

        generated_answers = extract_json_block(raw_output)

        for key, value in generated_answers.items():
            job_data["result"][key] = value

        job_data["status"] = "done"
        job_data["error"] = None

    except Exception as e:
        job_data["status"] = "error"
        job_data["error"] = f"Failed to parse model output:\n{str(e)}"
