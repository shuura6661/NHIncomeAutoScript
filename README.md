# 🌟 NHIncomeAutoScript 🌟

Effortlessly claim your Ninja Income in the **Ninja Heroes** mobile game with this automated script!  
Say goodbye to manual work and let the script handle your income collection for you.

---

## 📋 Features

- 🛠 **Automated Income Claiming**: Automatically collect your Ninja Income with precision.
- ⚡ **Fast and Reliable**: Designed to work efficiently without interruptions.
- 🎮 **For Ninja Heroes Fans**: Tailored for players of the Ninja Heroes mobile game.

---

## 🚀 Getting Started

Follow these steps to set up and use the script:

### Prerequisites
- Ensure **Python 3.7+** is installed on your system.
- Required Python packages:
  - `requests`
  - `beautifulsoup4`

Install them using:
```bash
pip install -r requirements.txt

---

Installation
Clone the repository:

bash
Copy code
git clone https://github.com/shuura6661/NHIncomeAutoScript.git
cd NHIncomeAutoScript
Install the required dependencies:

bash
Copy code
pip install -r requirements.txt
Configure your settings by updating the config.json file:

json
Copy code
{
  "username": "your_username",
  "password": "your_password"
}
You're ready to go! Run the script with:

bash
Copy code
python claim_income.py
⚙️ Configuration
You can configure the script by editing the config.json file. Make sure to enter your Ninja Heroes account credentials and adjust any other settings to suit your needs.

Example config.json:
json
Copy code
{
  "username": "your_username",
  "password": "your_password",
  "claim_interval": 600
}
"username": Your Ninja Heroes account username.
"password": Your Ninja Heroes account password.
"claim_interval": The interval (in seconds) between each claim action. Default is 600 seconds (10 minutes).
📦 How it Works
The script logs into your Ninja Heroes account using the credentials provided.
It navigates to the income claim page.
The script automatically claims your Ninja Income at the specified interval.
You can monitor the process through the console for updates.
📖 Usage
Once the script is running, it will continuously claim your Ninja Income based on the configured interval. You can stop the script at any time using Ctrl + C in your terminal.

Example Output:
bash
Copy code
[*] Logging in as: your_username
[*] Claiming income...
[*] Income claimed successfully!
[*] Next claim in 10 minutes...
🛠️ Troubleshooting
If you encounter any issues, try the following steps:

Ensure your Python version is 3.7 or higher.
Make sure all dependencies are installed correctly (pip install -r requirements.txt).
Double-check your config.json for correct account credentials.
For detailed error messages, check the log output in the terminal.
If the issue persists, feel free to open an issue on the GitHub Issues page.
