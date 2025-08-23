// Theme toggle
// Theme toggle
const themeToggle = document.getElementById("theme-toggle");
if (themeToggle) {
    themeToggle.addEventListener("click", () => {
        document.body.classList.toggle("dark");
        themeToggle.textContent = document.body.classList.contains("dark")
            ? "☀️ Light Mode"
            : "🌙 Dark Mode";
    });
}

// Fetch server stats
async function fetchStats() {
    try {
        const res = await fetch("/api/stats");
        if (!res.ok) return;
        const data = await res.json();

        document.getElementById("cpu").textContent = data.cpu;
        document.getElementById("ram").textContent = data.ram;
        document.getElementById("download").textContent = data.download;
        document.getElementById("upload").textContent = data.upload;
        document.getElementById("ftp-user").textContent = data.ftp_user || "admin";
        document.getElementById("ftp-pass").textContent = data.ftp_pass || "12345";
        document.getElementById("web-port").textContent = data.web_port;
    } catch (err) {
        console.error("Error fetching stats:", err);
    }
}

// Refresh stats every 5 seconds
setInterval(fetchStats, 5000);
fetchStats();




// ------------------------------
// 🔥 Hot Reload Lite
// ------------------------------
let lastModified = null;

async function checkForChanges() {
    try {
        const res = await fetch(window.location.pathname, { method: "HEAD" });
        const modified = res.headers.get("last-modified");

        if (lastModified && modified !== lastModified) {
            console.log("🔄 Changes detected, reloading...");
            window.location.reload(true);
        }
        lastModified = modified;
    } catch (err) {
        console.error("Hot reload check failed:", err);
    }
}

// Check every 5 seconds for file updates
setInterval(checkForChanges, 5000);
