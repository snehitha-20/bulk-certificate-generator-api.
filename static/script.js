
const form = document.getElementById("certificateForm");
const recipientsContainer = document.getElementById("recipients");
const message = document.getElementById("message");
const results = document.getElementById("results");
const jobsContainer = document.getElementById("jobs");
const generateButton = document.getElementById("generateButton");

document.getElementById("addRecipient").addEventListener("click", () => {
    const row = document.createElement("div");
    row.className = "recipient";

    row.innerHTML = `
        <input class="recipient-name" type="text"
               placeholder="Recipient name" required>
        <input class="recipient-email" type="email"
               placeholder="Email address" required>
    `;

    recipientsContainer.appendChild(row);
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const recipients = Array.from(
        recipientsContainer.querySelectorAll(".recipient")
    ).map(row => ({
        name: row.querySelector(".recipient-name").value.trim(),
        email: row.querySelector(".recipient-email").value.trim()
    }));

    const payload = {
        event_name: document.getElementById("eventName").value.trim(),
        event_date: document.getElementById("eventDate").value,
        recipients
    };

    generateButton.disabled = true;
    message.textContent = "Generating certificates...";
    results.replaceChildren();

    try {
        const response = await fetch("/jobs", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            const details = Array.isArray(data.detail)
                ? data.detail.map(item =>
                    `${item.loc?.join(".")}: ${item.msg}`
                  ).join("\n")
                : data.detail || "Request failed";

            throw new Error(details);
        }

        message.textContent =
            `Job status: ${data.status}\n` +
            `Total: ${data.total} | Succeeded: ${data.succeeded} | Failed: ${data.failed}`;

        (data.certificates || []).forEach(certificate => {
            const item = document.createElement("div");
            item.className = "result-item";

            const title = document.createElement("strong");
            title.textContent =
                certificate.name || certificate.certificate_id;

            const status = document.createElement("p");
            status.textContent = `Status: ${certificate.status}`;

            item.append(title, status);

            if (certificate.status === "SUCCEEDED") {
                const link = document.createElement("a");
                link.className = "download-link";
                link.href =
                    `/certificates/${encodeURIComponent(certificate.certificate_id)}/download`;
                link.textContent = "Download PDF";
                item.appendChild(link);
            }

            results.appendChild(item);
        });

        if (!data.certificates?.length) {
            results.textContent = "The job returned no certificate records.";
        }

        await loadJobs();
    } catch (error) {
        message.textContent = `Error: ${error.message}`;
    } finally {
        generateButton.disabled = false;
    }
});

async function loadJobs() {
    jobsContainer.textContent = "Loading jobs...";

    try {
        const response = await fetch("/jobs");

        if (!response.ok) {
            throw new Error("Could not retrieve jobs");
        }

        const data = await response.json();
        jobsContainer.replaceChildren();

        if (!data.jobs?.length) {
            jobsContainer.textContent = "No previous jobs found.";
            return;
        }

        data.jobs.forEach(job => {
            const item = document.createElement("div");
            item.className = "job-item";

            const title = document.createElement("strong");
            title.textContent = job.event_name;

            const details = document.createElement("p");
            details.textContent =
                `Date: ${job.event_date} | Status: ${job.status}`;

            const counts = document.createElement("p");
            counts.className = "muted";
            counts.textContent =
                `Total: ${job.total} | Succeeded: ${job.succeeded} | Failed: ${job.failed}`;

            const view = document.createElement("button");
            view.type = "button";
            view.className = "secondary";
            view.textContent = "View job details";
            view.addEventListener("click", () => viewJob(job.id));

            item.append(title, details, counts, view);
            jobsContainer.appendChild(item);
        });
    } catch (error) {
        jobsContainer.textContent = error.message;
    }
}

async function viewJob(jobId) {
    try {
        const response = await fetch(`/jobs/${encodeURIComponent(jobId)}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Could not load job details");
        }

        message.textContent =
            `Job: ${data.event_name}\n` +
            `Job ID: ${data.id}\n` +
            `Status: ${data.status}\n` +
            `Total: ${data.total} | Succeeded: ${data.succeeded} | Failed: ${data.failed}`;
    } catch (error) {
        message.textContent = `Error: ${error.message}`;
    }
}

document.getElementById("refreshJobs").addEventListener("click", loadJobs);

loadJobs();
