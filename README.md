<p align="center">
  <img src="images/logo1.png" alt="PayLog Logo" width="120"/>
</p>

<h1 align="center">PayLog</h1>
<p align="center"><b>Modern Point of Sale App built with KivyMD</b></p>

---

## 📱 About PayLog

**PayLog** is a modern, user-friendly Point of Sale (POS) application built with [KivyMD](https://github.com/kivymd/KivyMD). It helps you manage menu items, tables, sales, and financial reports efficiently for your business. PayLog is designed for both Android and desktop platforms.

---

## 🚀 Features

- **Menu Management:** Add, search, and manage menu items with images and prices.
- **Shopping Cart:** Add items to cart, adjust quantity, and process payments.
- **Table Management:** Add, update status, and view table order history.
- **Sales Report:** Export sales reports to Excel files, saved directly to the Download folder.
- **Multi-Platform:** Works on Android and Desktop (Windows/Linux/Mac).

---

## 🛠️ Installation

1. **Clone this repository:**
   ```sh
   git clone https://github.com/yourusername/paylog.git
   cd paylog
   ```

2. **(Optional) Create a virtual environment:**
   ```sh
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```sh
   python main.py
   ```

---

## 📦 Build for Android

Make sure you have [Buildozer](https://github.com/kivy/buildozer) installed:

```sh
buildozer -v android debug
```

The APK will be available in the `bin/` folder.

---

## 📁 Project Structure

- `main.py` — Main application logic.
- `main.kv` — KivyMD UI definitions.
- `db_manager.py` — SQLite database management.
- `images/` — Logo & menu images.
- `requirements.txt` — Python dependencies.

---

## 📃 License

This project is licensed under a **Custom Proprietary License**.  
Use, modification, and redistribution are **not permitted** without explicit written permission from the copyright holder.

For full license details, please see the [LICENSE.md](./LICENSE.md) file.

---