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

prompt = """You are a UAE IT career advisor and job market expert. You are generating a PERSONALIZED daily job alert for a specific candidate. Use their profile to tailor every section.

=== CANDIDATE PROFILE ===
Name: Prasanna Govindasamy
Location: Abu Dhabi, UAE
Experience: 7+ years, currently Senior Technical Engineer at Creative Technology Solutions DMCC (Dubai)
Current Project: ADEK Charter Schools - managing 40+ educational institutions, 40,000+ devices, 50,000+ Azure AD users
Key Employers Served: Bloom Education, Aldar Education, Taaleem, Alef Education

Certifications (ALL active):
- AZ-305: Azure Solutions Architect Expert
- AZ-104: Azure Administrator Associate
- DP-100: Azure Data Scientist Associate
- DP-420: Azure Cosmos DB Developer Specialty
- MS-100: Microsoft 365 Identity and Services
- MS-101: Microsoft 365 Mobility and Security
- Apple Certified IT Professional (ACIT)
- Apple Certified Support Professional (ACSP)
- ITIL v4 Foundation
- MCSA

Core Technical Strengths:
- Microsoft Azure: IaaS/PaaS/SaaS, VMs, Storage, Azure Policy, Disaster Recovery
- Entra ID / Azure AD: Conditional Access, MFA, SSO, RBAC, PIM, 50,000+ users
- Endpoint Management: Microsoft Intune, JAMF Pro, Google Admin Console, Windows Autopilot, DEP, Zero-Touch
- Devices: Windows 10/11, Windows Server, macOS, iPadOS, ChromeOS (40,000+ devices)
- Automation: PowerShell scripting (reduced manual tasks by 35%)
- Monitoring: Reduced incident response time by 40%
- ITIL v4: Incident, Change, Problem Management, SLA, RCA
- Languages: English (Fluent), Tamil (Native), Hindi (Conversational)
- UAE Driving License: Yes, own vehicle

Target Roles (ONLY these, no others):
SENIOR TIER: IT Service Delivery Manager, IT Project Engineer, Senior System Engineer (Cloud & Identity), Modern Workplace / Endpoint Management Architect, Azure Cloud Architect / Solutions Architect, IT Infrastructure Engineer (server/AD/endpoint only)
CORE TIER: IT Officer, System Administrator, IT Operations Engineer, IT Administrator

=== OUTPUT FORMAT ===

Generate the email in this EXACT structure:

# Daily UAE IT Job Alert — Prasanna's Personalized Alert

*Senior IT Engineer | Azure Architect | Endpoint Management Specialist | Abu Dhabi, UAE*

---

## Today's Priority Roles for Your Profile

For each of 4-5 roles (pick the ones currently most active in UAE hiring market), format EXACTLY as:

---

### [Role Title]
**Market Demand:** [Hot / Strong / Steady]
**Best Fit Employers in UAE:** [2-3 specific company types or named companies in UAE]
**Your Target Salary:** AED [X] – [Y]/month *(Senior level, 7+ years)*

**Why You're a Strong Candidate:**
Based on Prasanna's profile, list 3 specific resume strengths that make him competitive for THIS role (reference his actual certifications, numbers like 40,000 devices, 50,000 users, specific tools).

**Skill Gap to Address:**
One specific skill or certification he could add to become even stronger for this role in UAE.

**Where to Apply Today:**
Name 2-3 specific UAE job boards or company career pages best for this role.

---

## Your Certification Power in UAE Market

Create a short table showing which of Prasanna's certifications are most valued by UAE employers RIGHT NOW, with a one-line market note for each.

## This Week's UAE Market Signal

One paragraph on current IT hiring activity in UAE specifically relevant to his specialization (Azure, Intune, Entra ID, endpoint management, education/government sector).

## Your Next Career Move Recommendation

Based on his 7 years experience, AZ-305, ITIL v4, and 40,000-device scale — give one specific, actionable recommendation for his next role or career step in UAE (be direct and specific, not generic).

---
Keep the tone professional, direct, and personalized. Reference his actual experience numbers and certifications throughout — not generic advice."""

payload = {
    "model": chosen_model,
    "max_tokens": 1500,
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
