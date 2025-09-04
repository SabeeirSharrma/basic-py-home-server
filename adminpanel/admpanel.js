// ADMIN PANEL SCRIPT DO NOT EDIT

// ===== Theme Toggle =====
const themeToggle = document.getElementById("theme-toggle");
if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark");
    themeToggle.textContent = document.body.classList.contains("dark")
      ? "☀️ Light Mode"
      : "🌙 Dark Mode";
  });
}

// ===== Helpers =====
function mb(n) { return Math.round(n); }
function toMbps(bitsPerSec) { return (bitsPerSec / 1e6).toFixed(2) + " Mbps"; }

// ===== Stats =====
async function fetchStats() {
  try {
    const res = await fetch("/stats");
    if (!res.ok) return;
    const d = await res.json();

    document.getElementById("cpu").textContent = d.cpu_usage.toFixed(1);

    const ramText = `${mb(d.ram_used_mb)} / ${mb(d.ram_total_mb)} MB (${d.ram_percent.toFixed(1)}%)`;
    document.getElementById("ram").textContent = ramText;

    // optional: show instantaneous net i/o (if you add spans for them)
    if (document.getElementById("download")) {
      document.getElementById("download").textContent =
        typeof d.net_down_bps === "number" ? toMbps(d.net_down_bps * 8) : "N/A";
    }
    if (document.getElementById("upload")) {
      document.getElementById("upload").textContent =
        typeof d.net_up_bps === "number" ? toMbps(d.net_up_bps * 8) : "N/A";
    }
  } catch (e) {
    console.error("stats failed", e);
  }
}

// ===== Speedtest (active) =====
async function fetchSpeedtest() {
  try {
    const res = await fetch("/speedtest");
    if (!res.ok) return;
    const d = await res.json();
    if (d.error) {
      document.getElementById("download").textContent = "Error";
      document.getElementById("upload").textContent = "Error";
    } else {
      if (typeof d.download === "number") {
        document.getElementById("download").textContent = toMbps(d.download);
      }
      if (typeof d.upload === "number") {
        document.getElementById("upload").textContent = toMbps(d.upload);
      }
    }
  } catch (e) {
    console.error("speedtest failed", e);
  }
}

// ===== Settings (FTP + ports) =====
async function fetchSettings() {
  try {
    const res = await fetch("/settings");
    if (!res.ok) return;
    const s = await res.json();
    if (document.getElementById("web-port")) {
      document.getElementById("web-port").textContent = s.web_port ?? "8080";
    }
    if (document.getElementById("ftp-user")) {
      document.getElementById("ftp-user").textContent = s.ftp_user || "admin";
    }
    if (document.getElementById("ftp-pass")) {
      document.getElementById("ftp-pass").textContent = s.ftp_pass || "anonymous";
    }
  } catch (e) {
    console.error("settings failed", e);
  }
}

// ===== Init =====
fetchSettings();               // once at start
fetchStats();                  // immediately
setInterval(fetchStats, 2000); // every 2s
// Optional: also hit /speedtest every minute (comment out if you prefer the instantaneous psutil rates)
setInterval(fetchSpeedtest, 60000);