# 🚀 NETCUP QUICKSTART - Copy & Paste Commands

Server is ready! Just need to install SSH client.

---

## ⚡ FASTEST WAY - Install OpenSSH:

### 1. Open PowerShell AS ADMIN (Right-click Start → Terminal Admin)

```powershell
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```

### 2. Close admin window, open NORMAL PowerShell:

```powershell
cd C:\HutterLab
```

### 3. First connection (type 'yes' when asked):

```powershell
ssh root@37.120.185.27
# Password: lFuhbQZ3O1FQKV2
# Type: yes (to accept fingerprint)
# Then: exit
```

### 4. Run auto script:

```powershell
.\SIMPLE_AUTO_SETUP.ps1
```

**Done! It will:**
- Upload setup script (10 sec)
- Install everything on server (15 min)
- Upload enwik9 data (5-10 min)
- Upload models (1 min)
- Start compression!

---

## 📋 MANUAL COMMANDS (if auto fails):

### Upload files:
```powershell
scp C:\HutterLab\netcup_setup.sh root@37.120.185.27:/root/
scp C:\HutterLab\data\enwik9_reordered_transformed root@37.120.185.27:/root/
scp C:\HutterLab\paq8px\build\english.rnn root@37.120.185.27:/root/
scp C:\HutterLab\paq8px\build\x86_64.rnn root@37.120.185.27:/root/
```

### Connect and setup:
```powershell
ssh root@37.120.185.27
```

Then on server:
```bash
# Setup
bash /root/netcup_setup.sh

# Move files to correct locations
mv /root/enwik9_reordered_transformed /root/hutter/paq8px/
mv /root/english.rnn /root/hutter/paq8px/build/
mv /root/x86_64.rnn /root/hutter/paq8px/build/

# Start compression
cd /root/hutter/paq8px
screen -S compression
./paq8px -5r enwik9_reordered_transformed final_netcup.paq8

# Detach: Ctrl+A then D
```

---

## 🎯 Server Info:

```
IP: 37.120.185.27
Password: lFuhbQZ3O1FQKV2
OS: Debian 13
```

When asked about fingerprint, type: **yes**

Expected fingerprint (ED25519):
`SHA256:RZOfihaVg+ECdtpKra6vDS9SsmctqjIoPN5zrjReJUw`

---

**Start here:** Install SSH → Run SIMPLE_AUTO_SETUP.ps1 → Done! 🎄
