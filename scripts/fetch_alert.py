import urllib.request
import urllib.error
import json
import os
import datetime

api_key = os.environ.get("ANTHROPIC_API_KEY", "")
github_output = os.environ.get("GITHUB_OUTPUT", "")

# ── helpers ──────────────────────────────────────────────────────────────────

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

# ── model selection ───────────────────────────────────────────────────────────

PREFERRED_MODELS = [
        "claude-sonnet-4-5",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-haiku-20240307",
]

models_data, err = api_request("/v1/models")
chosen_model = PREFERRED_MODELS[-1]          # safe fallback
if models_data:
        available = {m["id"] for m in models_data.get("data", [])}
        for candidate in PREFERRED_MODELS:
                    if candidate in available:
                                    chosen_model = candidate
                                    break

            print(f"Using model: {chosen_model}", flush=True)

# ── today's date for freshness signal ────────────────────────────────────────

today_str = datetime.date.today().strftime("%d %B %Y")

# ── system prompt (role + rules) ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are a senior UAE IT recruitment specialist and career advisor.
Your ONLY job is to produce a structured, recruiter-style daily job alert email for the
candidate described in the user message.

ABSOLUTE RULES:
1. Never fabricate apply links. If a direct URL is unavailable, write N/A and note the source.
2. Evaluate each role with exactly 4-6 recruiter-style bullet points referencing the
   candidate's REAL numbers (40,000 devices, 50,000 users, 40% incident reduction, 35%
      automation gain) and REAL certifications (AZ-305, AZ-104, MS-100, MS-101, ITIL v4,
         ACIT, ACSP, DP-420, DP-100, MCSA).
         3. Output a CSV-compatible job table using the pipe-delimited format specified.
         4. Scope: UAE-only roles, last 7 days where known.
         5. Focus solely on the candidate's target role categories — no off-topic suggestions.
         6. Tone: professional, direct, recruiter-level — no generic filler."""

# ── main user prompt ──────────────────────────────────────────────────────────

prompt = f"""Today's date: {today_str}

    === CANDIDATE CV SUMMARY ===
    Name: Prasanna Govindasamy
    Location: Abu Dhabi, UAE | +971 52-2450153
    Current Role: Senior Technical Engineer, Creative Technology Solutions DMCC (Dubai) — Jul 2021–Present
    Project: ADEK Charter Schools — 40+ institutions, 40,000+ devices (Windows/macOS/iPadOS/ChromeOS),
             50,000+ Azure AD/Entra ID users
             Key Clients: Bloom Education, Aldar Education, Taaleem, Alef Education, New Century Education
             Education: B.E. Electronics & Communications, Anna University 2014

             CERTIFICATIONS (all active):
             AZ-305 | AZ-104 | DP-100 | DP-420 | MS-100 | MS-101 | ACIT | ACSP | ITIL v4 Foundation | MCSA

             CORE SKILLS:
             - Azure: IaaS/PaaS/SaaS, VMs, Storage, Entra ID, Conditional Access, MFA, SSO, RBAC, PIM,
                      Azure Policy, Disaster Recovery, Azure Site Recovery
                      - Endpoint: Intune, JAMF Pro, Apple School Manager, Google Admin Console, Autopilot,
                                  Apple DEP, Zero-Touch Deployment, MAM, MDM
                                  - OS: Windows 10/11 Enterprise, Windows Server, macOS, iPadOS, ChromeOS
                                  - Automation: PowerShell (35% manual task reduction), Batch scripting
                                  - ITSM: ITIL v4, Incident/Change/Problem Mgmt, SLA, RCA
                                  - Networking: VPN, Firewall, NSG, Virtual Networks
                                  - Monitoring: Reduced incident response time by 40%
                                  - Languages: English (Fluent), Tamil (Native), Hindi (Conversational)
                                  - UAE Driving License + own vehicle

                                  TARGET ROLES:
                                  SENIOR TIER: IT Service Delivery Manager | IT Project Engineer | Senior Systems Engineer
                                               (Cloud & Identity) | Modern Workplace / Endpoint Management Architect |
                                                            Azure Cloud / Solutions Architect | IT Infrastructure Engineer
                                                            CORE TIER: IT Officer | System Administrator | IT Operations Engineer | IT Administrator

                                                            === INSTRUCTIONS ===

                                                            Produce a daily job alert email in the following EXACT sections:

                                                            ---

                                                            ## SECTION 1 — SUMMARY ASSESSMENT

                                                            Write a concise 5-bullet overall market assessment for Prasanna's profile today, referencing
                                                            his actual metrics and certifications. Cover: overall positionin
