"""Quick test to check if the Gemini API key is valid and has available quota."""
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv(Path(__file__).resolve().parent / ".env")

MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
]

def test_model(client, model_name):
    try:
        response = client.models.generate_content(model=model_name, contents="Say 'ok'")
        print(f"  [OK]   {model_name} — response: {response.text.strip()[:60]}")
        return True
    except Exception as exc:
        msg = str(exc)
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
            print(f"  [QUOTA] {model_name} — quota exhausted")
        elif "404" in msg or "not found" in msg.lower():
            print(f"  [N/A]  {model_name} — model not available")
        elif "403" in msg or "API_KEY" in msg or "PERMISSION" in msg:
            print(f"  [AUTH] {model_name} — invalid API key or permission denied")
        else:
            print(f"  [ERR]  {model_name} — {type(exc).__name__}: {msg[:120]}")
        return False

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[FAIL] GEMINI_API_KEY is not set in .env or environment.")
        return

    print(f"[INFO] API key found: {api_key[:8]}...")
    client = genai.Client(api_key=api_key)

    print("[INFO] Testing models:\n")
    working = []
    for model in MODELS:
        if test_model(client, model):
            working.append(model)

    print()
    if working:
        print(f"[RESULT] Working models: {', '.join(working)}")
    else:
        print("[RESULT] No models available — check quota or API key.")

if __name__ == "__main__":
    main()
