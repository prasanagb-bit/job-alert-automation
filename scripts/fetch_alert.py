import urllib.request
import urllib.error
import json
import os

api_key = os.environ.get("ANTHROPIC_API_KEY", "")
github_output = os.environ.get("GITHUB_OUTPUT", "")

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
        print(f"HTTP {e.code} on {path}: {raw}", flush=True)
        return None, raw
    except Exception as e:
        print(f"Exception on {path}: {e}", flush=True)
        return None, str(e)

# Auto-discover model
models_data, err = api_request("/v1/models")
if models_data:
    model_ids = [m["id"] for m in models_data.get("data", [])]
    claude_models = [m for m in model_ids if "claude" in m.lower()]
    chosen_model = claude_models[0] if claude_models else "claude-3-haiku-20240307"
else:
    chosen_model = "claude-3-haiku-20240307"

print(f"Using model: {chosen_model}", flush=True)

prompt = """You are a UAE IT job market expert. Generate a professional daily job alert email for an IT professional in the UAE targeting ONLY these specific roles:

SENIOR / SPECIALIST TIER:
- IT Service Delivery Manager
- IT Project Engineer
- Senior System Engineer (Cloud & Identity)
- Modern Workplace / Endpoint Management Architect
- Azure Cloud Architect / Solutions Architect
- IT Infrastructure Engineer (server/AD/endpoint focused ONLY)

CORE OPERATIONS TIER:
- IT Officer
- System Administrator / Sysadmin
- IT Operations Engineer
- IT Administrator

Format as:

# Daily UAE IT Job Alert

## Today's Hot Roles in UAE

List 4-6 of the above roles currently in demand in UAE (Dubai, Abu Dhabi, Sharjah). For each role:
- Role title
- Typical employer type (banking, government, tech company, telecom)
- Salary range in AED/month
- Key skills required (3-4 points)
- One-line tip for standing out in UAE market

## UAE Job Portals to Check Today
Top 4 platforms for UAE IT jobs (Bayt, LinkedIn UAE, GulfTalent, Naukrigulf).

## UAE Market Insight
One paragraph on current IT hiring trends in UAE focused on cloud, identity, endpoint management, service delivery.

## Today's Action Tip
One specific actionable tip for applying to IT roles in UAE (visa, salary negotiation, certifications valued in UAE).

Keep it professional, UAE-specific, and motivating."""

payload = {
    "model": chosen_model,
    "max_tokens": 1200,
    "messages": [{
        "role": "user",
        "content": prompt
    }]
}

result, err = api_request("/v1/messages", payload)
if result and "content" in result:
    message = result["content"][0]["text"]
    print("SUCCESS - Got Claude response", flush=True)
else:
    message = f"API Error: {err}"
    print(f"Failed - {err}", flush=True)

if github_output:
    with open(github_output, "a", encoding="utf-8") as f:
        f.write("message<<EOF\n")
        f.write(message + "\n")
        f.write("EOF\n")
