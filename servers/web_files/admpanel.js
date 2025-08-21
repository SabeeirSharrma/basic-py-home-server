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

        // Update system stats
        document.getElementById("cpu").textContent = data.cpu;
        document.getElementById("ram").textContent = data.ram;
        document.getElementById("download").textContent = data.download;
        document.getElementById("upload").textContent = data.upload;

        // FTP info (fallback to defaults if missing)
        document.getElementById("ftp-user").textContent = data.ftp_user || "admin";
        document.getElementById("ftp-pass").textContent = data.ftp_pass || "12345";

        // Current server port (from backend or browser)
        if (data.web_port) {
            document.getElementById("server-port").textContent = data.web_port;
        } else {
            document.getElementById("server-port").textContent = window.location.port || "80";
        }
    } catch (err) {
        console.error("Error fetching stats:", err);
    }
}

// Refresh stats every 5 seconds
setInterval(fetchStats, 5000);
fetchStats();
