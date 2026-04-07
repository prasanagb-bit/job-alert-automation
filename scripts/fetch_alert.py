import urllib.request
import urllib.error
import json
import os
import sys

api_key = os.environ.get("ANTHROPIC_API_KEY", "")
github_output = os.environ.get("GITHUB_OUTPUT", "")

if not api_key:
    message = "Error: ANTHROPIC_API_KEY secret is not set."
else:
    payload = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Generate a daily job alert summary for software engineering roles. "
                    "Include 3-5 trending job titles, key skills in demand, and a motivational tip "
                    "for job seekers. Keep it concise and professional."
                )
            }
        ]
    }

    body = json.dumps(payload).encode("utf-8")

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
            data = json.loads(raw)
            message = data["content"][0]["text"]
            print("SUCCESS: Claude responded.")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        print("HTTP Error body:", raw, file=sys.stderr)
        try:
            err = json.loads(raw)
            message = "API Error: " + err.get("error", {}).get("message", raw)
        except Exception:
            message = "API HTTP Error: " + raw
    except Exception as e:
        message = "Unexpected error: " + str(e)
        print(message, file=sys.stderr)

if github_output:
    with open(github_output, "a", encoding="utf-8") as f:
        f.write("message<<EOF\n")
        f.write(message + "\n")
        f.write("EOF\n")
else:
    print(message)
