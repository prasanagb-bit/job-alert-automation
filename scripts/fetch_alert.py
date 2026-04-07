import urllib.request
import urllib.error
import json
import os

api_key = os.environ.get("ANTHROPIC_API_KEY", "")
github_output = os.environ.get("GITHUB_OUTPUT", "")

print(f"DEBUG: API key prefix: {api_key[:15] if api_key else 'EMPTY'}", flush=True)

def api_request(path, body=None):
    url = "https://api.anthropic.com" + path
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url=url, data=data, method="POST" if body else "GET")
    req.add_header("x-api-key", api_key)
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        print(f"DEBUG: HTTP {e.code} on {path}: {raw}", flush=True)
        return None, raw
    except Exception as e:
        print(f"DEBUG: Exception on {path}: {e}", flush=True)
        return None, str(e)

# Step 1: List available models
print("DEBUG: Fetching available models...", flush=True)
models_data, err = api_request("/v1/models")
if models_data:
    model_ids = [m["id"] for m in models_data.get("data", [])]
    print(f"DEBUG: Available models: {model_ids}", flush=True)
    # Pick the first claude model available
    claude_models = [m for m in model_ids if "claude" in m.lower()]
    chosen_model = claude_models[0] if claude_models else "claude-3-haiku-20240307"
else:
    print(f"DEBUG: Could not list models ({err}), using default", flush=True)
    chosen_model = "claude-3-haiku-20240307"

print(f"DEBUG: Using model: {chosen_model}", flush=True)

# Step 2: Call the messages API
payload = {
    "model": chosen_model,
    "max_tokens": 512,
    "messages": [{
        "role": "user",
        "content": "Generate a daily job alert for software engineers: list 3-5 trending roles, top skills needed, and one motivational tip. Be concise."
    }]
}

result, err = api_request("/v1/messages", payload)
if result and "content" in result:
    message = result["content"][0]["text"]
    print("DEBUG: SUCCESS - Got Claude response", flush=True)
else:
    message = f"API Error: {err}"
    print(f"DEBUG: Failed - {err}", flush=True)

print(f"DEBUG: Message preview: {message[:100]}", flush=True)

if github_output:
    with open(github_output, "a", encoding="utf-8") as f:
        f.write("message<<EOF\n")
        f.write(message + "\n")
        f.write("EOF\n")
