function showOutput(title, data) {
    const box = document.getElementById("task-output");
    const logs = document.getElementById("logs-panel");

    const status = data.status || "unknown";
    const stdout = (data.stdout || "").trim();
    const stderr = (data.stderr || "").trim();

    if (status === "success") {
        box.style.borderColor = "#238636";
        box.style.color = "#c6f6d5";
    } else if (status === "error") {
        box.style.borderColor = "#f85149";
        box.style.color = "#fca5a5";
    } else {
        box.style.borderColor = "#30363d";
        box.style.color = "#eee";
    }

    let lines = [];
    lines.push(`=== ${title} (${status.toUpperCase()}) ===`);

    if (stdout) {
        lines.push("");
        lines.push("STDOUT:");
        lines.push(stdout);
    }

    if (stderr && stderr !== "No errors reported.") {
        lines.push("");
        lines.push("STDERR:");
        lines.push(stderr);
    }

    if (!stdout && (!stderr || stderr === "No errors reported.")) {
        lines.push("");
        lines.push("No output returned from Ansible.");
    }

    box.textContent = lines.join("\n");
    logs.textContent = stdout + "\n\n" + stderr;
}

function showLoading(title) {
    const box = document.getElementById("task-output");
    box.style.borderColor = "#30363d";
    box.style.color = "#eee";
    box.textContent = `=== ${title} ===\n\nRunning, please wait...`;

    const logs = document.getElementById("logs-panel");
    logs.textContent = "Waiting for logs...";
}

function runHealthCheck() {
    showLoading("Health Check");
    fetch("http://localhost:5000/api/health-check/run")
        .then(r => r.json())
        .then(data => showOutput("Health Check", data))
        .catch(err => showOutput("Health Check", { status: "error", stdout: "", stderr: String(err) }));
}

function runPatch() {
    showLoading("Patch & Reboot");
    fetch("http://localhost:5000/api/patch/run")
        .then(r => r.json())
        .then(data => showOutput("Patch & Reboot", data))
        .catch(err => showOutput("Patch & Reboot", { status: "error", stdout: "", stderr: String(err) }));
}

function runSecurity() {
    showLoading("Security Scan");
    fetch("http://localhost:5000/api/security/run")
        .then(r => r.json())
        .then(data => showOutput("Security Scan", data))
        .catch(err => showOutput("Security Scan", { status: "error", stdout: "", stderr: String(err) }));
}

function runBackup() {
    showLoading("Backup");
    fetch("http://localhost:5000/api/backup/run")
        .then(r => r.json())
        .then(data => showOutput("Backup", data))
        .catch(err => showOutput("Backup", { status: "error", stdout: "", stderr: String(err) }));
}

function askAI() {
    const questionBox = document.getElementById("ai-question");
    const responseBox = document.getElementById("ai-response");
    const question = questionBox.value.trim();

    if (!question) {
        responseBox.textContent = "Please type a question for NimbusAI.";
        return;
    }

    responseBox.textContent = "Thinking...";

    fetch("http://localhost:5000/api/ai/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question })
    })
    .then(r => r.json())
    .then(data => {
        responseBox.textContent = data.answer || "NimbusAI did not return an answer.";
    })
    .catch(err => {
        responseBox.textContent = "Error talking to NimbusAI: " + String(err);
    });
}




