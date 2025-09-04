# 🏠 Basic Python Home Server

A lightweight **home server** built with Python, providing:
- 🌍 Static web hosting  
- 📂 FTP file sharing  
- ⚙️ Admin panel with live system stats  

Perfect for learning, experimenting, or running a small home network project.

---

## 📦 Features

- **Web Server** (HTTP)  
  - Serves static files from `./servers/web_files`  
  - Hot reload support for quick development  

- **FTP Server**  
  - Accessible with custom credentials  
  - Root directory: `./servers/web_files` (so web files and FTP files stay in sync)  

- **Admin Panel**  
  - Hosted on its own port (default: `9090`)  
  - Shows:
    - FTP credentials  
    - Current web server port  
    - CPU usage  
    - RAM usage  
    - Upload / download speed (via `speedtest-cli`)  
  - Dark/light theme toggle  

---

## 📂 Project Structure

