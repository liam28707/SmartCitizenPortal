# SmartCitizenPortal
AI-powered Odoo module for smart citizen complaint management with automated classification, prioritization, and workflow tracking for government services.

# 🚀 Setup Instructions

## 1. Install Odoo

First, follow the official Odoo installation guide for your operating system:

👉 https://www.odoo.com/documentation

Make sure Odoo is fully installed and runnable before proceeding.

---

## 2. Clone Required Repositories

Navigate to the directory where Odoo is installed, then clone the Odoo tutorials repository:

```bash
git clone https://github.com/odoo/tutorials
```

Next, clone this project (your repo) into the same directory (or inside your custom addons folder):

```bash
git clone <YOUR_REPO_LINK>
```

---

## 3. Add Custom Module to Odoo

Ensure your module is inside a directory listed in Odoo’s `addons_path`.

Example:

```bash
addons_path = /path/to/odoo/addons,/path/to/odoo/tutorials,/path/to/your_repo
```

---

## 4. Set Up Mistral API Key

This project uses Mistral AI for automatic classification.

You must set your API key as an environment variable:

---

### 🐧 Linux / 🍎 macOS

```bash
export MISTRAL_API_KEY="your_api_key_here"
```

To see if it is added:

* `echo $MISTRAL_API_KEY`

---

### 🪟 Windows (Command Prompt)

```cmd
setx MISTRAL_API_KEY "your_api_key_here"
```

Restart your terminal after setting this.

---

### 🪟 Windows (PowerShell)

```powershell
$env:MISTRAL_API_KEY="your_api_key_here"
```

---

## 5. Run Odoo

Navigate to your Odoo directory and run:

### 🐧 Linux / 🍎 macOS

```bash
./odoo-bin --addons-path=addons,../tutorials/ -d rd-demo -u smart_citizen_portal --dev xml
```

### 🪟 Windows

```cmd
python odoo-bin -c odoo.conf
```

---

## 6. Install the Module

1. Open Odoo in your browser: http://localhost:8069
2. Enable **Developer Mode**
3. Go to **Apps**
4. Click **Update Apps List**
5. Search for your module (e.g., *Smart Citizen Portal*)
6. Click **Install**

---

## ✅ You're Ready!

You should now be able to:

* Create citizen requests
* Use AI-powered categorization
* View dashboards and analytics

---

## ⚠️ Troubleshooting

* Ensure `MISTRAL_API_KEY` is set correctly
* Restart Odoo after making changes
* Check logs for errors:

  ```bash
  tail -f odoo.log
  ```

---

## 💡 Notes

* Requires Python 3.11 and PostgreSQL
* Make sure dependencies (e.g., `requests`) are installed:

  ```bash
  pip install requests
  ```

---
