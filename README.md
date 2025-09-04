# 🏠 Basic Python Home Server

![GitHub last commit (branch)](https://img.shields.io/github/last-commit/SabeeirSharrma/Basic-py-home-server/main)
![GitHub forks](https://img.shields.io/github/forks/SabeeirSharrma/Basic-py-home-server)
![GitHub Release](https://img.shields.io/github/v/release/SabeeirSharrma/basic-py-home-server)


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

## Dependencies/Minimum Requirements
   [Python 3.10+](https://python.org) 
   lib: rich psutil pyftpdlib flask livereload speedtest-cli
   run `pip install rich psutil pyftpdlib flask livereload speedtest-cli` in cmd after Python (with pip) installation

   **Requirements:**
  | Component| Min|
  | -----------------|:-------------:|
  | CPU|AMD Ryzen 7 4800H or better (intel supported)|
  | RAM|4GB DDR4 or better|
  | OS| Windows 10 / comparable linux or better|


  Basically **most** mid-range server builds can handle this
   
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
