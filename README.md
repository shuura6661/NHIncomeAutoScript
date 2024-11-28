# 🌟 NHIncomeAutoScript 🌟

Effortlessly claim your Ninja Income in the **Ninja Heroes** mobile game with this automated script!  
Say goodbye to manual work and let the script handle your income collection for you.

---

## 📋 Features

- 🛠 **Automated Income Claiming**: Automatically collect your Ninja Income with precision.
- ⚡ **Fast and Reliable**: Designed to work efficiently without interruptions.
- 🎮 **For Ninja Heroes Fans**: Tailored for players of the Ninja Heroes mobile game.
- 🔒 **Secure**: Keeps your credentials safe by using a secure configuration.
- 🔧 **Customizable**: Adjust settings, server names, or other configurations as needed.

---

## 🚀 Getting Started

Follow these steps to set up and use the script:

### Prerequisites
- Ensure **Python 3.7+** is installed on your system.
- Required Python packages:
  - `requests` - Handles HTTP requests.
  - `beautifulsoup4` - Parses HTML data from the game.

Install them using:
```bash
pip install -r requirements.txt
```

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/shuura6661/NHIncomeAutoScript.git
   cd NHIncomeAutoScript
   ```

2. Add your credentials to the configuration file (`config.json`):
   ```json
   {
       "email": "your_email@gmail.com",
       "password": "your_password",
       "server_name": "your_server"
   }
   ```
   - Replace `your_email@gmail.com`, `your_password`, and `your_server` with your Ninja Heroes login details.
   - Ensure the file is securely saved and not shared publicly.

3. Run the script:
   ```bash
   python main.py
   ```

4. Monitor the output:
   - The script will log its progress in the console, including successful claims.

---

## 🖼️ Screenshots
<p align="center">
  <img src="assets/screenshot1.png" alt="Script Running Example" width="600px">
  <br>
  <i>Example of the script running successfully.</i>
</p>

---

## 🛠 Troubleshooting

### Common Issues
1. **Authentication Failed**:
   - Double-check your credentials in `config.json`.
   - Ensure you have internet access.
   
2. **Dependencies Missing**:
   - Make sure all required Python packages are installed:
     ```bash
     pip install -r requirements.txt
     ```

3. **Unexpected Errors**:
   - Run the script in debug mode (if implemented) or check for typos.

---

## 🛡️ License

This project is licensed under the **MIT License**. You are free to use, modify, and distribute this project. See the [LICENSE](LICENSE) file for more details.

---

## 🤝 Contributing

We welcome contributions to enhance this project! Here's how you can contribute:
1. **Fork the Repository**: Create a copy of the repository on your account.
2. **Create a New Branch**: Add your features or fixes:
   ```bash
   git checkout -b feature/NewFeature
   ```
3. **Submit a Pull Request**: Once your changes are complete, submit a PR with a detailed description.

---

## 📧 Contact

For questions, suggestions, or feedback, feel free to contact us:
- **GitHub**: [@shuura6661](https://github.com/shuura6661)
- **Email**: shuura6661@example.com (if applicable)

---

<p align="center">Made with ❤️ for Ninja Heroes fans!</p>
