import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import ast
import base64

# Function to get base64 of an image
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_img_with_href(local_img_path):
    img_format = local_img_path.split('.')[-1]
    binary_val = get_base64_of_bin_file(local_img_path)
    return f'data:image/{img_format};base64,{binary_val}'

# Set page config for a premium feel
st.set_page_config(
    page_title="Netflix Analytics | Insights Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Constants
NETFLIX_RED = "#E50914"
NETFLIX_DARK = "#0e1117"
NETFLIX_GREY = "#222222"
WHITE = "#FFFFFF"

# Custom CSS for Premium Design & Single-Page Fit
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    
    .stApp {{
        background-color: {NETFLIX_DARK};
        color: {WHITE};
    }}
    
    /* Reduce top padding */
    .block-container {{
        padding-top: 0.1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }}
    
    /* Sticky Sidebar Style */
    section[data-testid="stSidebar"] {{
        background-color: {NETFLIX_GREY};
        border-right: 1px solid #333;
    }}
    /* Compact Glassmorphism Charts with No Scrollbars */
    .stPlotlyChart {{
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 5px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 5px !important;
        overflow: hidden !important;
    }}
    
    .stPlotlyChart > div {{
        overflow: hidden !important;
        background: transparent !important;
    }}

    /* Hide Streamlit elements but KEEP sidebar toggle */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}
    
    /* Compact Header */
    .header-container {{
        display: flex;
        align-items: center;
        gap: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid {NETFLIX_RED};
        margin-bottom: 20px;
    }}
    
    /* Metric Card Styling - Compact */
    div[data-testid="stMetric"] {{
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 5px 10px !important;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
        min-height: 60px !important;
    }}
    
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.08);
        border-color: {NETFLIX_RED};
    }}
    
    div[data-testid="stMetricValue"] {{
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
        color: {NETFLIX_RED} !important;
    }}
    
    div[data-testid="stMetricLabel"] {{
        font-size: 0.7rem !important;
        color: #BBB !important;
        margin-bottom: 0px !important;
        line-height: 1 !important;
    }}
    
    /* Ensure metric content fits */
    div[data-testid="stMetric"] > div {{
        padding: 0 !important;
    }}
    
    
    h1, h2, h3 {{
        color: {WHITE};
        font-weight: 700;
        margin-top: 0px !important;
        margin-bottom: 10px !important;
    }}
    
    .stSubheader {{
        font-size: 1.1rem !important;
    }}
</style>
""", unsafe_allow_html=True)

# Helper to parse list-like columns
def parse_list_col(val):
    try:
        if isinstance(val, str) and val.startswith('['):
            return ast.literal_eval(val)
        return val
    except:
        return val

@st.cache_data
def load_data():
    titles_df = pd.read_csv("titles.csv") if os.path.exists("titles.csv") else pd.DataFrame()
    credits_df = pd.read_csv("credits.csv") if os.path.exists("credits.csv") else pd.DataFrame()
    
    if titles_df.empty:
        return pd.DataFrame(), pd.DataFrame()
        
    column_mapping = {
        'production_countries': 'country',
        'genres': 'listed_in'
    }
    titles_df = titles_df.rename(columns=column_mapping)
    
    if 'date_added' in titles_df.columns:
        titles_df['date_added'] = pd.to_datetime(titles_df['date_added'].str.strip(), format='%B %d, %Y', errors='coerce')
        titles_df['year_added'] = titles_df['date_added'].dt.year
    else:
        titles_df['year_added'] = titles_df['release_year']
        
    for col in ['country', 'listed_in']:
        if col in titles_df.columns:
            titles_df[col] = titles_df[col].apply(parse_list_col)
            
    return titles_df, credits_df

try:
    df, credits_df = load_data()
    if df.empty:
        st.error("Essential dataset 'titles.csv' not found.")
        st.stop()

    # Sidebar (Filters)
    with st.sidebar:
        st.subheader("Advanced Filters")
        
        # Core Selection
        content_types = sorted(df['type'].unique())
        content_selection = st.multiselect(
            "Content Type",
            options=content_types,
            default=list(content_types)
        )
        
        years = st.slider(
            "Release Years",
            min_value=int(df['release_year'].min()),
            max_value=int(df['release_year'].max()),
            value=(int(df['release_year'].min()), int(df['release_year'].max()))
        )
        
        st.markdown("---")
        
        # Search Box
        search_query = st.text_input("🔍 Search Titles", placeholder="e.g. Breaking Bad")
        
        # Genre Multi-select (Exploded)
        all_genres = sorted(list(df['listed_in'].explode().dropna().unique()))
        selected_genres = st.multiselect("Filter by Genre", options=all_genres)
        
        # Country Multi-select (Exploded)
        all_countries = sorted(list(df['country'].explode().dropna().unique()))
        selected_countries = st.multiselect("Filter by Country", options=all_countries)
        
        # Sorting
        st.markdown("---")
        sort_by = st.selectbox("Sort Library By", options=["Release Year", "Title", "IMDb Score"])
        
        st.markdown("---")
        if st.checkbox("Show Data Explorer"):
            st.session_state['show_explorer'] = True
        else:
            st.session_state['show_explorer'] = False

    # --- Filtering Logic ---
    filtered_df = df[
        (df['type'].isin(content_selection)) &
        (df['release_year'].between(years[0], years[1]))
    ]
    
    # Apply Search
    if search_query:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search_query, case=False, na=False)]
        
    # Apply Genre Filter
    if selected_genres:
        filtered_df = filtered_df[filtered_df['listed_in'].apply(lambda x: any(g in x for g in selected_genres) if isinstance(x, list) else False)]
        
    # Apply Country Filter
    if selected_countries:
        filtered_df = filtered_df[filtered_df['country'].apply(lambda x: any(c in x for c in selected_countries) if isinstance(x, list) else False)]

    # Apply Sorting
    sort_map = {"Release Year": "release_year", "Title": "title", "IMDb Score": "imdb_score"}
    if sort_map[sort_by] in filtered_df.columns:
        filtered_df = filtered_df.sort_values(by=sort_map[sort_by], ascending=(sort_by == "Title"))
    # --- Header Section (Centered Row) ---
    try:
        logo_base64 = get_img_with_href("assets/logo.png")
    except:
        logo_base64 = ""

    st.markdown(f"""
        <div style="display: flex; flex-direction: row; align-items: center; justify-content: center; width: 100%; gap: 15px; margin-bottom: 5px;">
            <img src="{logo_base64}" width="50">
            <div style="text-align: left; border-left: 2px solid {NETFLIX_RED}; padding-left: 15px;">
                <h1 style="margin: 0; padding: 0; font-size: 2rem; color: {WHITE}; letter-spacing: 1px; font-weight: 800; line-height: 1;">
                    NETFLIX <span style="color: {NETFLIX_RED};">ANALYTICS</span>
                </h1>
                <p style="margin: 0; padding: 0; color: #BBB; font-size: 0.8rem; font-weight: 400; letter-spacing: 0.5px; margin-top: 2px;">
                    Unveiling Content Trends & Library Insights
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Preserve state for static charts (Genre Composition)
    base_filtered_df = filtered_df.copy()

    # --- Row 1: Header Slicer (Genre Pills Master) ---
    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
    _, pill_col, _ = st.columns([1, 4, 1])
    with pill_col:
        top_genres_master = ["All"] + sorted(list(df['listed_in'].explode().value_counts().head(8).index))
        selected_pill = st.pills(
            "Explore by Genre",
            options=top_genres_master,
            selection_mode="single",
            default="All",
            key="genre_pills_master"
        )
    if selected_pill and selected_pill != "All":
        filtered_df = filtered_df[filtered_df['listed_in'].apply(lambda x: selected_pill in x if isinstance(x, list) else False)]

    # --- Row 1: Metrics, Trend & Genre Split (3 Columns) ---
    col_kpi, col_trend, col_sun = st.columns([1, 1.5, 1])
    
    with col_kpi:
        st.markdown(f"<h3 style='font-size: 0.85rem; color: {NETFLIX_RED}; margin-bottom: 8px; text-transform: uppercase;'>Library Overview</h3>", unsafe_allow_html=True)
        # 2x2 Grid for compact KPIs
        k_r1_c1, k_r1_c2 = st.columns(2)
        k_r2_c1, k_r2_c2 = st.columns(2)
        with k_r1_c1: st.metric("Library", f"{len(filtered_df):,}")
        with k_r1_c2: 
            m_count = len(filtered_df[filtered_df['type'].str.upper().str.contains('MOVIE', na=False)])
            st.metric("Movies", f"{m_count:,}")
        with k_r2_c1:
            tv_count = len(filtered_df[filtered_df['type'].str.upper().str.contains('SHOW', na=False)])
            st.metric("TV Shows", f"{tv_count:,}")
        with k_r2_c2:
            ratio = round(m_count / tv_count, 1) if tv_count > 0 else "N/A"
            st.metric("M:S Ratio", f"{ratio}:1" if ratio != "N/A" else "N/A")

    with col_trend:
        if 'year_added' in filtered_df.columns:
            trend_df = filtered_df.groupby('year_added').size().reset_index(name='count')
            trend_df = trend_df[trend_df['count'] > 0]
            trend_df.columns = ['Year', 'Titles Added']
            
            st.markdown(f"<h3 style='font-size: 0.85rem; color: {NETFLIX_RED}; margin-bottom: 5px; text-transform: uppercase;'>Acquisition Trend</h3>", unsafe_allow_html=True)
            fig_trend = px.area(
                trend_df, x='Year', y='Titles Added', line_shape='spline',
                color_discrete_sequence=[NETFLIX_RED]
            )
            fig_trend.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                xaxis=dict(title=None, gridcolor='#333'), yaxis=dict(title=None, gridcolor='#333'),
                margin=dict(t=5, b=25, l=10, r=10), height=140
            )
            fig_trend.update_traces(fillcolor='rgba(229, 9, 20, 0.3)', hovertemplate="<b>Year: %{x}</b><br>Titles: %{y}<extra></extra>")
            st.plotly_chart(fig_trend, use_container_width=True)

    with col_sun:
        # Sunburst uses base_filtered_df (ignores genre pills)
        sun_df = base_filtered_df[['type', 'listed_in']].explode('listed_in')
        top_type_genres = sun_df.groupby(['type', 'listed_in']).size().reset_index(name='count')
        top_type_genres = top_type_genres.sort_values(['type', 'count'], ascending=[True, False])
        top_type_genres = top_type_genres.groupby('type').head(5).reset_index(drop=True)

        st.markdown(f"<h3 style='font-size: 0.85rem; color: {NETFLIX_RED}; margin-bottom: 8px; text-transform: uppercase;'>Genre Split</h3>", unsafe_allow_html=True)
        fig_sun = px.sunburst(
            top_type_genres, path=['type', 'listed_in'], values='count', color='type',
            color_discrete_map={'MOVIE': NETFLIX_RED, 'SHOW': "#444444", 'Movie': NETFLIX_RED, 'TV Show': "#444444"}
        )
        fig_sun.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
            margin=dict(t=0, b=0, l=0, r=0), height=140
        )
        fig_sun.update_traces(hovertemplate="<b>%{label}</b><br>Titles: %{value}<extra></extra>")
        st.plotly_chart(fig_sun, use_container_width=True)

    # --- Row 2: Cast, Actors & Directors (Talent Hub) ---
    col_cast, col_act, col_dir = st.columns(3)
    
    # Pre-calculate Top Cast
    filtered_ids = filtered_df['id'].unique()
    cast_counts = credits_df[(credits_df['id'].isin(filtered_ids)) & (credits_df['role'] == 'ACTOR')]
    cast_counts = cast_counts['name'].value_counts().head(5).reset_index()
    cast_counts.columns = ['Actor', 'Count']

    with col_cast:
        if not cast_counts.empty:
            st.markdown(f"<h3 style='font-size: 0.85rem; color: {NETFLIX_RED}; margin-bottom: 5px; text-transform: uppercase;'>Top Cast Distribution</h3>", unsafe_allow_html=True)
            fig_cast = px.bar(
                cast_counts, x='Count', y='Actor', orientation='h',
                color_discrete_sequence=[NETFLIX_RED]
            )
            fig_cast.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                xaxis=dict(title=None, gridcolor='#333'), yaxis=dict(title=None, gridcolor='#333', tickfont=dict(size=10), categoryorder='total ascending'),
                margin=dict(t=5, b=35, l=10, r=10), height=180
            )
            fig_cast.update_traces(hovertemplate="<b>%{y}</b><br>Titles: %{x}<extra></extra>")
            st.plotly_chart(fig_cast, use_container_width=True)

    with col_act:
        if not filtered_df.empty and not credits_df.empty:
            titles_lite = filtered_df[['id', 'imdb_score']]
            actors_lite = credits_df[credits_df['role'] == 'ACTOR'][['id', 'name']]
            merged_act = pd.merge(actors_lite, titles_lite, on='id')
            act_stats = merged_act.groupby('name').agg({'id': 'count', 'imdb_score': 'mean'}).reset_index()
            act_stats.columns = ['Actor', 'Titles', 'Score']
            top_actors = act_stats.sort_values(['Score', 'Titles'], ascending=False).head(5)
            
            if not top_actors.empty:
                st.markdown(f"<h3 style='font-size: 0.85rem; color: {NETFLIX_RED}; margin-bottom: 5px; text-transform: uppercase;'>Top Actors</h3>", unsafe_allow_html=True)
                fig_act = px.bar(
                    top_actors, x='Score', y='Actor', orientation='h',
                    color='Score', color_continuous_scale=[[0, "#333"], [1, NETFLIX_RED]]
                )
                fig_act.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                    xaxis=dict(title=None, gridcolor='#333', range=[0, 10]),
                    yaxis=dict(title=None, gridcolor='#333', categoryorder='total ascending'),
                    margin=dict(t=5, b=35, l=10, r=10), height=180, coloraxis_showscale=False
                )
                fig_act.update_traces(hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>", marker_line_width=0)
                st.plotly_chart(fig_act, use_container_width=True)

    with col_dir:
        if not filtered_df.empty and not credits_df.empty:
            titles_lite = filtered_df[['id', 'imdb_score']]
            dir_lite = credits_df[credits_df['role'] == 'DIRECTOR'][['id', 'name']]
            merged_dir = pd.merge(dir_lite, titles_lite, on='id')
            dir_stats = merged_dir.groupby('name').agg({'id': 'count', 'imdb_score': 'mean'}).reset_index()
            dir_stats.columns = ['Director', 'Titles', 'Score']
            top_dirs = dir_stats.sort_values(['Score', 'Titles'], ascending=False).head(5)
            
            if not top_dirs.empty:
                st.markdown(f"<h3 style='font-size: 0.85rem; color: {NETFLIX_RED}; margin-bottom: 5px; text-transform: uppercase;'>Top Directors</h3>", unsafe_allow_html=True)
                fig_dir = px.bar(
                    top_dirs, x='Score', y='Director', orientation='h',
                    color='Score', color_continuous_scale=[[0, "#333"], [1, NETFLIX_RED]]
                )
                fig_dir.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                    xaxis=dict(title=None, gridcolor='#333', range=[0, 10]),
                    yaxis=dict(title=None, gridcolor='#333', categoryorder='total ascending'),
                    margin=dict(t=5, b=35, l=10, r=10), height=180, coloraxis_showscale=False
                )
                fig_dir.update_traces(hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>", marker_line_width=0)
                st.plotly_chart(fig_dir, use_container_width=True)

    # --- Row 3: Maturity & Geography (2 Columns) ---
    col_mat_row3, col_geo = st.columns(2)
    
    with col_mat_row3:
        if 'age_certification' in filtered_df.columns:
            rating_counts = filtered_df['age_certification'].value_counts().reset_index()
            rating_counts.columns = ['Rating', 'Count']
            
            st.markdown(f"<h3 style='font-size: 0.85rem; color: {NETFLIX_RED}; margin-bottom: 5px; text-transform: uppercase;'>Maturity Profile</h3>", unsafe_allow_html=True)
            fig_rating = px.bar(
                rating_counts, x='Rating', y='Count',
                color_discrete_sequence=[NETFLIX_RED]
            )
            fig_rating.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                xaxis=dict(title=None, gridcolor='#333'), yaxis=dict(title=None, gridcolor='#333'),
                margin=dict(t=5, b=35, l=10, r=10), height=180
            )
            fig_rating.update_traces(hovertemplate="<b>Rating: %{x}</b><br>Titles: %{y}<extra></extra>")
            st.plotly_chart(fig_rating, use_container_width=True)

    with col_geo:
        if 'country' in filtered_df.columns:
            countries_series = filtered_df['country'].explode().dropna()
            country_counts = countries_series.value_counts().head(5).reset_index()
            country_counts.columns = ['Country', 'Count']
            
            st.markdown(f"<h3 style='font-size: 0.85rem; color: {NETFLIX_RED}; margin-bottom: 5px; text-transform: uppercase;'>Regional Presence</h3>", unsafe_allow_html=True)
            fig_country = px.bar(
                country_counts, x='Count', y='Country', orientation='h',
                color_discrete_sequence=[NETFLIX_RED]
            )
            fig_country.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                xaxis=dict(title=None, gridcolor='#333'), yaxis=dict(title=None, gridcolor='#333', tickfont=dict(size=10), categoryorder='total ascending'),
                margin=dict(t=5, b=35, l=60, r=10), height=180
            )
            fig_country.update_traces(hovertemplate="<b>%{y}</b><br>Titles: %{x}<extra></extra>")
            st.plotly_chart(fig_country, use_container_width=True)

    # --- Row 4: Strategic AI Insights ---
    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
    
    # Calculate Insights
    insights = []
    if not filtered_df.empty:
        # Genre Insight (Recalculate for insights)
        temp_genres = filtered_df['listed_in'].explode().value_counts().reset_index()
        temp_genres.columns = ['Genre', 'Count']
        
        if not temp_genres.empty:
            top_genre = temp_genres.iloc[0]['Genre']
            top_genre_pct = (temp_genres.iloc[0]['Count'] / len(filtered_df) * 100)
            insights.append(f"<b>{top_genre}</b> dominates the library, accounting for {top_genre_pct:.1f}% of selected titles.")
        
        # Trend Insight
        if 'year_added' in filtered_df.columns:
            # Re-ensure trend_df is defined or recalculate
            trend_data = filtered_df.groupby('year_added').size().reset_index(name='count')
            if not trend_data.empty:
                peak_year = trend_data.iloc[trend_data['count'].idxmax()]['year_added']
                insights.append(f"Content acquisition peaked in <b>{int(peak_year)}</b>, showing a significant library expansion phase.")
        
        # Rating Insight
        if 'age_certification' in filtered_df.columns:
            r_counts = filtered_df['age_certification'].value_counts().reset_index()
            if not r_counts.empty:
                top_rating = r_counts.iloc[0]['age_certification']
                insights.append(f"The primary audience segment is <b>{top_rating}</b>, indicating a focus on mature/adult content.")

    # Render Insights with Premium Styling
    insight_html = "".join([f"<div style='flex: 1; min-width: 200px; background: rgba(255,255,255,0.03); padding: 8px; border-radius: 8px; border-left: 3px solid {NETFLIX_RED}; margin: 3px;'><p style='margin:0; font-size: 0.8rem; color: {WHITE};'>{text}</p></div>" for text in insights])
    
    st.markdown(f"""
        <div style="background: rgba(255,255,255,0.05); padding: 8px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px);">
            <h3 style="margin: 0 0 5px 5px; font-size: 0.9rem; color: {NETFLIX_RED}; letter-spacing: 1px; font-weight: 700;">STRATEGIC INSIGHTS</h3>
            <div style="display: flex; flex-wrap: wrap; justify-content: space-between;">
                {insight_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Conditional Data Explorer
    if st.session_state.get('show_explorer', False):
        st.markdown("---")
        available_cols = [c for c in ['title', 'type', 'release_year', 'country', 'listed_in'] if c in filtered_df.columns]
        st.dataframe(filtered_df[available_cols].head(50), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Dashboard Error: {e}")
