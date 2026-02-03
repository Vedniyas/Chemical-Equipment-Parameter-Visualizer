# Chemical Equipment Visualizer

A full-stack hybrid application for analyzing chemical equipment data. This project consists of a Django Backend (API), a React Web Dashboard, and a PyQt5 Desktop Application.

## 🚀 Key Features
* **Advanced Data Processing:** Parses CSV files to calculate **Averages** and **Standard Deviation** (volatility) for Flowrate, Pressure, and Temperature.
* **Modern Web Dashboard:**
    * Interactive Charts (Bar & Pie) using Chart.js.
    * **Dynamic Navbar:** Features glassmorphism effects and scrolling transitions.
    * Responsive design for various screen sizes.
* **Desktop Application:** Native PyQt5 client for analyzing data outside the browser.
* **Local Development:** Fully configured to run on Localhost for rapid testing.

---

## 📂 Project Structure
* `backend/` - Django REST API & SQLite Database (Handles logic & math).
* `frontend_web/` - React.js Web Application (Vite) with proxy setup.
* `frontend_desktop/` - PyQt5 Python Desktop Application.

---

## 🛠️ Installation & Setup (Localhost)

To run the full project, you will need **3 separate terminals**.

### 1. Backend Setup (Django)
*The engine of the project. Must be running first.*

```bash
cd backend

# Create virtual environment (Optional but recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies (including new math libraries)
pip install -r requirements.txt
pip install pandas numpy django-cors-headers

# Run Migrations & Start Server
python manage.py migrate
python manage.py runserver