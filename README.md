# Netflix Analytics & Strategy Dashboard

## About This Project
This project is an interactive data analysis case study where I explored the Netflix titles dataset using **Python** and built a high-performance dashboard using **Streamlit**.

The goal was to simulate real-world data analyst tasks such as calculating content KPIs, analyzing library growth trends, identifying maturity patterns, and understanding global production footprints. 

The final result is a "Single-Page Command Center" that makes complex library insights easier to understand through dynamic visualizations and automated AI insights.

## Dataset
**File**: `titles.csv`

The dataset contains nearly **6,000 Netflix titles** (Movies and TV Shows) with detailed information about genres, ratings, and production origins.

**Main columns in the dataset include:**
*   **id** – Unique identifier for each title
*   **title** – Name of the movie or show
*   **type** – Category (MOVIE or SHOW)
*   **release_year** – Year the title was originally released
*   **age_certification** – Parental rating (e.g., PG, TV-MA, R)
*   **genres** – List of genres associated with the title
*   **production_countries** – Countries where the content was produced
*   **imdb_score** – User rating from IMDb
*   **year_added** – The year the content was added to the Netflix library

## Project Files
**netflix-dashboard**
│
├── app.py
├── titles.csv
├── requirements.txt
├── .gitignore
├── README.md
└── assets/
    └── logo.png

*   **app.py**: Contains the main Streamlit application logic, custom CSS, and Plotly visualization code.
*   **titles.csv**: The raw dataset used for the analysis.
*   **requirements.txt**: Lists the Python dependencies needed to run the app.
*   **assets/**: Stores branding elements like the official Netflix logo.

## Analysis Performed
During the analysis, I explored several strategic questions such as:

### Key Library Metrics
*   **Total Library Size**: Unified count of all available content.
*   **Volume by Type**: Breakdown of Movies vs. TV Shows.
*   **Movie-to-Show Ratio**: Understanding Netflix's portfolio balance.

### Content Trends
*   **Acquisition Velocity**: Yearly trends of content being added to the platform.
*   **Growth Hotspots**: Identifying years of aggressive library expansion.

### Category & Maturity Analysis
*   **Maturity Profile**: Distribution of age certifications across the library.
*   **Genre Composition**: A deep dive into the "Genre DNA" of the platform using nested Sunburst visualizations.

### Regional Analysis
*   **Top Production Hubs**: Identifying the leading countries contributing to the Netflix catalog.
*   **Global Footprint**: Analyzing how production origins have shifted over time.

## Skills Used
This project helped practice several important Data Engineering and Visualization concepts including:
*   **Data Cleaning & Parsing**: Handling list-like strings in CSV columns (Genres/Countries).
*   **Interactive Slicers**: Building a synchronized filtering system using Streamlit Pills.
*   **Advanced Plotly**: Customizing Sunburst, Area, and Bar charts for premium aesthetics.
*   **Custom UI/UX**: Using Vanilla CSS injection to create a branded, "strictly unscrollable" single-page layout.

## Dashboard
The Streamlit dashboard was created to present these insights visually in a premium environment.

**The dashboard includes:**
*   **KPI Cards**: High-level metrics for Library size, Movies, and TV Shows.
*   **Interactive Genre Slicer**: A centered pill-selection system that updates the entire page.
*   **Maturity & Composition Row**: Side-by-side comparison of ratings and genre distributions.
*   **Trends & Geography Row**: Analysis of library growth and top production countries.
*   **Strategic AI Insights**: Automated narrative summaries of the current data view.

## What I Learned
Working on this project helped me practice:
*   Building high-performance, interactive analytical apps in Python.
*   Transforming raw library data into actionable strategic insights.
*   Designing professional UI/UX for data dashboards.
*   Managing version control and deployment workflows via GitHub.

## Author
**Taha Soda**

*Aspiring Data Analyst | Currently building projects in Python, SQL, and Streamlit to bridge the gap between data and strategy.*
