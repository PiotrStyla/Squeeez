# 🚀 MANUAL SETUP GUIDE - Netcup VPS

## PROBLEM: SSH not installed on Windows

You need SSH/SCP to connect to server. Two options:

---

## OPTION A: Install OpenSSH (Recommended - Built into Windows)

### Step 1: Open PowerShell AS ADMINISTRATOR
```
Right-click Start Menu → Windows Terminal (Admin) or PowerShell (Admin)
```

### Step 2: Install OpenSSH Client
```powershell
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```

### Step 3: Close and reopen regular PowerShell
```
Then run: .\SIMPLE_AUTO_SETUP.ps1
```

---

## OPTION B: Download PuTTY (If OpenSSH fails)

### Download:
https://www.putty.org/
- Get: putty.exe, pscp.exe, plink.exe
- Put in: C:\Program Files\PuTTY\

---

## OPTION C: MANUAL COMMANDS (Copy-paste each one)

If you want to do it manually step-by-step:

### 1. Connect to server:
```
Server: 37.120.185.27
Password: lFuhbQZ3O1FQKV2

Use PuTTY GUI or command line SSH
```

### 2. On server, run this (paste all at once):
```bash
# Update system
apt update && apt upgrade -y

# Install tools
apt install -y build-essential g++ make wget git screen

# Create directories
mkdir -p /root/hutter
cd /root/hutter

# Clone PAQ8px
git clone https://github.com/hxim/paq8px.git
cd paq8px

# Compile
make -j8

# Create model directory
mkdir -p build

# Test
./paq8px
```

### 3. Upload files (use WinSCP or FileZilla):
```
Download WinSCP: https://winscp.net/

Upload to server:
- enwik9_reordered_transformed → /root/hutter/paq8px/
- english.rnn → /root/hutter/paq8px/build/
- x86_64.rnn → /root/hutter/paq8px/build/

Local files are in:
C:\HutterLab\data\
C:\HutterLab\paq8px\build\
```

### 4. Start compression (on server via SSH):
```bash
cd /root/hutter/paq8px
screen -S compression
./paq8px -5r enwik9_reordered_transformed final_netcup.paq8

# Detach: Ctrl+A then D
```

### 5. Monitor:
```bash
# Reconnect
ssh root@37.120.185.27

# Check process
ps aux | grep paq8px

# Check output
ls -lh /root/hutter/paq8px/*.paq8

# Attach to screen
screen -r compression
```

---

## QUICK FIX - Install SSH NOW:

Run PowerShell **AS ADMINISTRATOR** and paste:
```powershell
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```

Then close and run normal PowerShell:
```powershell
cd C:\HutterLab
.\SIMPLE_AUTO_SETUP.ps1
```

---

Server: 37.120.185.27
Password: lFuhbQZ3O1FQKV2
