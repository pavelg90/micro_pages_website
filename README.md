# 📊 Interest Calculator - FastAPI

A simple web application built with **FastAPI** that calculates simple interest based on user input.

## 🚀 Features
- ✅ FastAPI backend for handling form submissions
- ✅ Jinja2 templating for rendering dynamic web pages
- ✅ Simple UI with an input form and result display
- ✅ Lightweight and easy to deploy

---

## 📂 Project Structure
```
fastapi_app/
│── templates/          # HTML templates for UI
│   ├── index.html      # Home page with input form
│   ├── result.html     # Result page displaying interest calculation
│── main.py             # FastAPI app logic
│── requirements.txt    # Dependencies
│── README.md           # Project documentation
```

---

## 🔧 Installation & Setup

### 1️⃣ **Clone the Repository**
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2️⃣ **Create a Virtual Environment (Optional, but recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4️⃣ **Run the Application**
```bash
uvicorn main:app --reload
```

The app will be available at: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🖥️ Usage

1. Open the app in your browser.
2. Enter the **Principal Amount**, **Annual Interest Rate (%),** and **Time (Years)**.
3. Click **"Calculate"** to see the interest result.
4. The result page will display the computed interest.

---

## 📦 Dependencies

The required dependencies are listed in `requirements.txt`. They include:

- **FastAPI**
- **Jinja2**
- **Uvicorn**
