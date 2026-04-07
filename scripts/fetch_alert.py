import urllib.request
import urllib.error
import json
import os
import sys

api_key = os.environ.get("ANTHROPIC_API_KEY", "")
github_output = os.environ.get("GITHUB_OUTPUT", "")

# Debug: print key prefix so we can confirm correct key is loaded
if api_key:
    print(f"DEBUG: API key loaded, starts with: {api_key[:12]}...", flush=True)
else:
    print("DEBUG: API key is EMPTY!", flush=True)

payload = {
    "model": "claude-3-haiku-20240307",
    "max_tokens": 512,
    "messages": [
        {
            "role": "user",
            "content": "List 3 trending software engineering job titles and 3 key skills. Be brief."
        }
    ]
}

body = json.dumps(payload).encode("utf-8")
print(f"DEBUG: Sending payload: {json.dumps(payload)}", flush=True)

req = urllib.request.Request(
    url="https://api.anthropic.com/v1/messages",
    data=body,
    method="POST"
)
req.add_header("x-api-key", api_key)
req.add_header("anthropic-version", "2023-06-01")
req.add_header("Content-Type", "application/json")

try:
    with urllib.request.urlopen(req) as resp:
        raw = resp.read().decode("utf-8")
        print(f"DEBUG: Raw response: {raw}", flush=True)
        data = json.loads(raw)
        message = data["content"][0]["text"]
        print("SUCCESS: Got Claude response", flush=True)
except urllib.error.HTTPError as e:
    raw = e.read().decode("utf-8")
    print(f"DEBUG: HTTP {e.code} error body: {raw}", flush=True)
    try:
        err = json.loads(raw)
        message = "API Error: " + json.dumps(err)
    except Exception:
        message = "API HTTP Error raw: " + raw
except Exception as e:
    message = "Unexpected error: " + str(e)
    print(f"DEBUG: Exception: {e}", flush=True)

print(f"DEBUG: Final message to email: {message[:200]}", flush=True)

if github_output:
    with open(github_output, "a", encoding="utf-8") as f:
        f.write("message<<EOF\n")
        f.write(message + "\n")
        f.write("EOF\n")
