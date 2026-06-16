from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYBOOK_DIR = os.path.join(BASE_DIR, "playbooks")

LAST_TASK_OUTPUT = {
    "stdout": "",
    "stderr": "",
    "task": ""
}

def run_playbook(playbook):
    playbook_path = os.path.join(PLAYBOOK_DIR, playbook)

    try:
        # ⭐ IMPORTANT: Use remote.ini (NOT inventory.ini)
        inventory_path = os.path.join(BASE_DIR, "remote.ini")

        result = subprocess.run(
            ["ansible-playbook", "-i", inventory_path, playbook_path],
            capture_output=True,
            text=True
        )

        stdout = result.stdout.strip() or "No output returned from Ansible."
        stderr = result.stderr.strip() or "No errors reported."
        status = "success" if result.returncode == 0 else "error"

        LAST_TASK_OUTPUT["stdout"] = stdout
        LAST_TASK_OUTPUT["stderr"] = stderr
        LAST_TASK_OUTPUT["task"] = playbook

        return {
            "status": status,
            "stdout": stdout,
            "stderr": stderr
        }

    except Exception as e:
        return {
            "status": "error",
            "stdout": "",
            "stderr": f"Backend exception: {str(e)}"
        }

# -------------------------------
# API ROUTES
# -------------------------------

@app.get("/api/health-check/run")
def run_health_check():
    return jsonify(run_playbook("health_check.yml"))

@app.get("/api/patch/run")
def run_patch():
    return jsonify(run_playbook("patch_linux.yml"))

@app.get("/api/backup/run")
def run_backup():
    return jsonify(run_playbook("backup_configs.yml"))

@app.get("/api/harden/run")
def run_harden():
    return jsonify(run_playbook("harden_baseline.yml"))

# -------------------------------
# NimbusAI Assistant
# -------------------------------

@app.get("/api/ai/ask")
def ai_ask():
    question = request.args.get("question", "").strip().lower()

    if not question:
        return jsonify({"answer": "Please type a question for NimbusAI."})

    stdout = LAST_TASK_OUTPUT["stdout"]
    stderr = LAST_TASK_OUTPUT["stderr"]
    task = LAST_TASK_OUTPUT["task"]

    # Summaries
    if "summarize" in question or "summary" in question:
        answer = (
            f"Here is a summary of the last task ({task}):\n\n"
            f"- Key output: {stdout[:300]}...\n"
            f"- Errors: {stderr if stderr != 'No errors reported.' else 'None'}\n\n"
            "This summary helps you quickly understand the main results."
        )
        return jsonify({"answer": answer})

    # Troubleshooting
    if "why" in question or "error" in question or "fail" in question:
        if "No errors reported" in stderr:
            answer = (
                "The last task did not report any errors. "
                "Everything appears to have completed successfully."
            )
        else:
            answer = (
                "Based on the last task output, here are possible issues:\n\n"
                f"{stderr[:300]}...\n\n"
                "You may need to check permissions, missing packages, or invalid paths."
            )
        return jsonify({"answer": answer})

    # Next-step suggestions
    if "next" in question or "what should i do" in question:
        if "health" in task:
            answer = "Next step: run a security scan to validate system hardening."
        elif "security" in task:
            answer = "Next step: apply patches or review SSH configuration."
        elif "patch" in task:
            answer = "Next step: run a health check to confirm system stability."
        elif "backup" in task:
            answer = "Next step: verify backup integrity or store it offsite."
        else:
            answer = "You can run any task next — health, security, patch, or backup."
        return jsonify({"answer": answer})

    # Default fallback
    answer = (
        "NimbusAI can help with:\n"
        "- Summaries (e.g., 'Summarize the last task')\n"
        "- Troubleshooting (e.g., 'Why did this fail?')\n"
        "- Next steps (e.g., 'What should I do next?')\n\n"
        "Try asking one of those."
    )
    return jsonify({"answer": answer})

# -------------------------------
# Run Flask
# -------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)





