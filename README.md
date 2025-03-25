

# 🌐 Remote Control Project – Web-Based IoT Device Manager for ESP32

**Remote Control Project** is a Flask-based web application developed to control and monitor hardware devices powered by **ESP32 microcontrollers**.  
The system allows users to remotely manage smart devices like motors, temperature sensors, and lighting systems directly through a web panel.

This project bridges the gap between **web interfaces and physical hardware** by utilizing a central database as the communication point between the user and the ESP32-connected devices.

---

## 🚀 What Does It Do?

- Registers hardware devices to the system with custom ESP32 IDs and capabilities.
- Lets users control these devices via a web interface (on/off, value updates, etc).
- Stores every command/action in a database.
- A remote server or ESP32 reads from the DB and executes the appropriate physical operation.
- Includes **user and admin dashboards**, each with different access levels.
- Offers **individual and corporate registration options**.
- Ensures secure login via **Google reCAPTCHA v2**.
- Real-time communication through **WebSockets** using Flask-SocketIO.

---

## 🔑 Key Features

- ✅ Real-time device control from a browser  
- 🔐 Login system with CAPTCHA protection  
- ⚙️ ESP32-to-database communication bridge  
- 🧾 Role-based access: Admin vs. User  
- 🏢 Individual and company registration support  
- ☁️ AWS DynamoDB as NoSQL backend  
- 🔄 Device commands are read from DB and executed physically  
- 🔌 WebSocket integration for instant feedback

---

## 🧠 How It Works

1. Devices with ESP32 chips are connected to real-world sensors/actuators.
2. The device is registered in the system with a unique ID and capability set.
3. The user logs into the panel and sends a command (e.g. “Turn on motor”).
4. That command is written to AWS DynamoDB under that device's record.
5. The ESP32 listens to the DB, reads its commands, and performs the physical task.
6. Admins can view all devices; users can only access their own.

---

## 🛠️ Technologies Used

- **Backend:** Python, Flask, Flask-SocketIO  
- **Database:** AWS DynamoDB  
- **Frontend:** HTML, CSS, Vanilla JS  
- **Security:** Google reCAPTCHA v2  
- **Hardware:** ESP32 Microcontroller (connected to sensors/motors)  
- **Communication:** REST API + WebSocket

---

## 🧾 Project Structure

```
REMOTE_CONTROL_PROJECT/
├── app.py                 # Main Flask app & routes
├── DB_ITEM.py             # AWS DynamoDB interactions
├── create_table.py        # Table creation and setup
├── requirements.py        # Config keys (CAPTCHA, secret key, etc.)
├── test.py                # For dev/testing purposes
├── static/                # Frontend assets (CSS, JS, icons)
└── templates/             # HTML templates for login, admin, user
```

---

## 📸 Screenshots
<img src="https://i.imgur.com/AJZHPOs.png">

---

## ⚙️ Getting Started

### 1. Install Dependencies
```bash
pip install flask boto3 flask-socketio requests
```

### 2. Configure `requirements.py`
Set your:
- `app_secret_key`
- `data_sitekey` and `secret` for Google reCAPTCHA
- AWS credentials for DynamoDB

### 3. Run the App
```bash
python app.py
```

Then go to:  
[http://localhost:5000](http://localhost:5000)

---

## 🌐 System Flow Summary

1. User logs in via a secured login screen.
2. Chooses a device from their dashboard.
3. Sends control commands (e.g. "turn off light").
4. Commands are saved in DynamoDB.
5. The ESP32 listens for new changes and executes them in real life.
6. Admins can view and manage all registered devices & users.

---

## 👨‍💻 Developer

**Tolga Ersoy**  
🎓 Pamukkale University – Computer Engineering | Full Stack Developer

🐙 https://github.com/tolgaersoy07

---

## 🔒 Disclaimer

This project was developed as part of a summer internship. It is a **proof-of-concept** that demonstrates the integration of frontend/backend systems with hardware-level device control using cloud infrastructure and secure communication protocols.

