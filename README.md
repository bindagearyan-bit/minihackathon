# 🌿 EcoTrace | CARBONPULSE
### Campus Carbon Footprint Auditor

> **"Measure. Understand. Reduce."**

A premium SaaS-style web dashboard for Indian educational institutions to track, analyze, and reduce their campus carbon footprint. Built in support of **UN SDG 13 — Climate Action**.

---

## 🚀 Features

| Feature | Description |
|---|---|
| 📊 **KPI Dashboard** | Total CO₂e, per-student emission, energy cost & potential savings |
| 📈 **Carbon Analytics** | Scope 1, 2 & 3 breakdowns with historical trend charts |
| 🏆 **Carbon League** | Fair departmental leaderboard ranked by CO₂e **per student** |
| 🔍 **OCR Bill Scanner** | Upload MSEDCL bills with Tesseract OCR (English / मराठी / हिन्दी) |
| ⚡ **Anomaly Detection** | Statistical Z-score based energy anomaly alerts |
| 🍱 **Mess Carbon Score** | Meal-level carbon intensity ratings with Green Day initiative |
| 🎚️ **What-If Simulator** | Interactive sliders for PC shutdown, carpool & solar ROI |
| ☀️ **Solar Timing Tip** | Smart scheduling recommendations for peak solar hours |
| 🎯 **Recommendations** | AI-assisted actionable savings with simulate buttons |
| 📋 **NAAC / NIRF Report** | One-click NAAC Criterion VII green audit PDF generator |

---

## 🛠️ Tech Stack

- **HTML5** — Semantic structure
- **Vanilla CSS** — Custom design system with CSS variables
- **Vanilla JavaScript** — Hash-based SPA routing, Chart.js charts, interactive simulations
- **Chart.js** — Campus carbon trend (line), source breakdown (donut), anomaly (bar)
- **Lucide Icons** — Clean icon system
- **Tesseract OCR** *(backend-ready)* — Marathi / Hindi bill scanning workflow

---

## 📁 File Structure

```
minihack/
├── index.html       # Main SPA shell with all page views
├── styles.css       # Full design system (dark forest-green SaaS theme)
├── app.js           # Router, charts, OCR simulation, simulator logic
└── .gitignore
```

---

## 🎓 Context

Designed for **D. Y. Patil College of Engineering** (demo institution) as a hackathon prototype for a campus-wide sustainability management platform.

**The platform flow:**
```
DATA → MEASURE → ANALYZE → DETECT → RECOMMEND → SIMULATE → REDUCE → REPORT
```

---

## 🌍 UN SDG Alignment

**SDG 13 — Climate Action**: Helps Indian educational institutions measure, track and actively reduce their institutional carbon footprint through data-driven decision making.

---

## 🚦 Getting Started

```bash
# Serve locally (Python)
python -m http.server 8080

# Open in browser
http://localhost:8080
```

No build step required — pure HTML/CSS/JS.

---

*Built with ❤️ for Indian campus sustainability.*
