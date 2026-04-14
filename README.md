# ⏳ Time Nest

**Master your time, build your routine, and find your focus.**

Time Nest is a streamlined, web-based productivity ecosystem. It bridges the gap between simple to-do lists and complex habit trackers by offering a unified, minimal interface designed to minimize cognitive load and maximize deep work.

---

## 🚀 Core Pillars:
Time Nest is built around four core pillars that work together to support sustainable productivity:
### ✅ Task Management
Organize your day with precision. Create, prioritize, and check off tasks as you go. The interface is built to give you a clear overview of your "Next Actions" without the clutter.

### 🔥 Habit Tracking
Consistency is the key to growth. Track your daily rituals and watch your streaks grow.
* **Visual Progress:** See your consistency at a glance.
* **Streak Protection:** Stay motivated by maintaining your daily momentum.

### 🧠 Focus Mode
Enter a distraction-free environment tailored for deep work.
* **Minimalist UI:** All non-essential elements vanish.
* **Timed Sessions:** Work in focused sprints to avoid burnout.

### 📊 Personal Dashboard
Your command center. Get a holistic view of your productivity data, task completion rates, and active habits in one unified snapshot.

---

## 🛠️ Technology Stack

TimeNest is designed for high performance and scalability using a modern serverless architecture.

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Backend** | Python / Flask | Serverless API & Business Logic |
| **Frontend** | Vanilla JS / HTML5 / CSS3 | Premium, high-performance UI |
| **Auth** | Firebase Auth | Secure, multi-platform authentication |
| **Database** | Google Firestore | Real-time, scalable NoSQL database |
| **Hosting** | Vercel | Global edge deployment |

---

## ☁️ Deployment

### 1. Vercel (Recommended)
This project is configured for one-click deployment to Vercel. 
1. Push this repository to GitHub.
2. Connect your GitHub repository to [Vercel](https://vercel.com).
3. Add the following **Environment Variables** in the Vercel Dashboard:
   - `FIREBASE_SERVICE_ACCOUNT_JSON`: The full JSON content of your Firebase Service Account key.
   - `JWT_SECRET_KEY`: A random string for securing tokens.
   - `FIREBASE_PROJECT_ID`: Your Firebase Project ID.

### 2. Local Development
1. Clone the repository.
2. Create a virtual environment: `python -m venv .venv`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Create a `.env` file based on `.env.example`.
5. Run the backend: `python -m backend.app`.
6. Open `http://localhost:5000` in your browser.


