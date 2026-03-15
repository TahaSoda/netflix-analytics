# 🎬 Netflix Analytics Dashboard

A premium, high-performance Netflix data visualization dashboard built with **Streamlit**, **Plotly**, and **Pandas**. This dashboard provides a sleek, "Single-Page Command Center" view of the Netflix library, featuring interactive genre filtering and strategic AI insights.

---

## ✨ Key Features

- **🚀 Single-Page Optimization**: Strictly unscrollable layout designed to fit perfectly on a single 1080p screen.
- **🎨 Premium Netflix Aesthetic**: Custom CSS for glassmorphism effects, Netflix red accents, and a refined dark theme.
- **🧩 Interactive Genre Slicer**: Centered "Pill" selection system that synchronizes instantly with all KPIs and charts.
- **📊 Advanced Visualizations**:
  - **Maturity Profile**: Distribution of content by age certification.
  - **Acquisition Trend**: Time-series area chart of content library growth.
  - **Global Geography**: Top 5 production countries.
  - **Genre Composition**: Static-reference Sunburst chart for global library context.
- **🤖 Strategic AI Insights**: Dynamic, automated insights generated based on current filter selections.

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Visualizations**: [Plotly Express](https://plotly.com/python/plotly-express/)
- **Data Processing**: [Pandas](https://pandas.pydata.org/)
- **Styling**: Vanilla CSS (Injected via Streamlit)

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have Python 3.8+ installed.

### 2. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/TahaSoda/netflix-analytics.git
cd netflix-analytics
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
streamlit run app.py
```

---

## ☁️ Deployment

This project is pre-configured for **Streamlit Community Cloud**.

1. Push this repository to your GitHub account.
2. Log in to [share.streamlit.io](https://share.streamlit.io/).
3. Connect your repository and deploy the `app.py` file.

---

## 📂 Project Structure

- `app.py`: Main application code and styling.
- `titles.csv`: Dataset containing Netflix movie and show information.
- `assets/`: Folder containing branding assets (e.g., Netflix logo).
- `requirements.txt`: Python dependencies.
- `.gitignore`: Files excluded from version control.

---

Developed with ❤️ for Netflix Enthusiasts.
