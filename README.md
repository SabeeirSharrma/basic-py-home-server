# 🏠 Basic Python Home Server

![GitHub last commit (branch)](https://img.shields.io/github/last-commit/SabeeirSharrma/Basic-py-home-server/main)
![GitHub forks](https://img.shields.io/github/forks/SabeeirSharrma/Basic-py-home-server)
![GitHub Release](https://img.shields.io/github/v/release/SabeeirSharrma/basic-py-home-server)
+

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

│── main.py # Entry point, starts all servers
│── server_manager.py # Manages starting/stopping servers
│── settings.txt # Config file for ports & credentials
│── login.txt # (optional) For login auth (currently unused)
│── admin_panel.py # Admin panel server
│
├── adminpanel/
│ ├── admpanel.html # Admin dashboard
│ ├── admpanel.css # Styles for panel
│ ├── admpanel.js # Panel logic (refresh stats, theme toggle, etc.)
│
├── servers/
│ ├── web_server.py # Web server (serves web_files)
│ ├── ftp_server.py # FTP server
│ └── web_files/ # Your hosted website
│ ├── index.html
│ └── ...

## CLI
This program has a built-in **CLI** for various purposes:
  `stop`  - Stop all servers
  `help / ?` - Show this help
  `ftp edit -user={username} -pass={password}`
     → Change FTP credentials (use -pass=* to remove password)
  `web set -port={PORT}`
     → Change the web server port dynamically
  `admin set -port={PORT}`
     → Change the admin panel port dynamically
     
## Webpages
To create/add pages to your site go to `YOUR_DIR/basic-py-home-server/servers/web_files`
**`index.html` is your home/landing page**
**Any HTML/CSS/JS file added will be hosted**
**To use Tailwind simply link it to your HTML file**

---

## ⚙️ Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/sabplay/basic-py-home-server.git
   cd basic-py-home-server
   ```
2. **Run `start.bat`***

## Config

**For Configs you can either edit settings.txt:**
```
web_port=8080      # Web server port
ftp_port=21        # FTP server port
ftp_user=admin     # FTP username
ftp_pass=12345     # FTP password
admin_port=9090    # Admin panel port
```
**OR**
**Use the CLI:**
  ftp edit -user={username} -pass={password}
     → Change FTP credentials (use -pass=* to remove password)
  web set -port={PORT}
     → Change the web server port dynamically
  admin set -port={PORT}
     → Change the admin panel port dynamically
