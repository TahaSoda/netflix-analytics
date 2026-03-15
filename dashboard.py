import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import ast
import base64

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
# Zero-CSS Refactor: Relying on native Streamlit theme and layouts

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
    # --- Deep Intelligence Engine ---
    deep_insights = []
    if not filtered_df.empty:
        # 1. Genre Opportunity Analysis (Hidden Gems)
        genre_stats = filtered_df.explode('listed_in').groupby('listed_in').agg({
            'id': 'count',
            'imdb_score': 'mean'
        }).reset_index()
        genre_stats.columns = ['Genre', 'Count', 'AvgScore']
        
        high_quality_niche = genre_stats[(genre_stats['Count'] <= genre_stats['Count'].median()) & 
                                        (genre_stats['AvgScore'] >= genre_stats['AvgScore'].quantile(0.75))]
        if not high_quality_niche.empty:
            best_niche = high_quality_niche.sort_values('AvgScore', ascending=False).iloc[0]
            deep_insights.append(f"**OPPORTUNITY MAP:** '{best_niche['Genre']}' is a high-performing niche (Avg Score: {best_niche['AvgScore']:.1f}) with low volume—potential for original content expansion.")

        # 2. Creator Impact & Efficiency
        if not credits_df.empty:
            f_ids = filtered_df['id'].unique()
            f_credits = credits_df[credits_df['id'].isin(f_ids)]
            dir_stats = f_credits[f_credits['role'] == 'DIRECTOR'].merge(filtered_df[['id', 'imdb_score']], on='id')
            dir_perf = dir_stats.groupby('name')['imdb_score'].mean().reset_index()
            if not dir_perf.empty:
                top_perf_dir = dir_perf.sort_values('imdb_score', ascending=False).iloc[0]
                deep_insights.append(f"**CREATOR IMPACT:** Director **{top_perf_dir['name']}** maintains a top-tier rating average (IMDb: {top_perf_dir['imdb_score']:.1f}) across selected titles.")

        # 3. Format Strategy
        format_split = filtered_df['type'].value_counts()
        if len(format_split) > 1:
            movie_pct = (format_split.get('MOVIE', 0) / len(filtered_df)) * 100
            strategy_desc = "Movie-heavy" if movie_pct > 60 else "Series-focused" if movie_pct < 40 else "Balanced"
            deep_insights.append(f"**STRATEGY PULSE:** The library currently shows a **{strategy_desc}** posture ({movie_pct:.0f}% Movies) for this segment.")

    insight_text = "\n".join([f"* {text}" for text in deep_insights]) if deep_insights else "No specific patterns detected."

    # --- Header Section (100% Native Python) ---
    head_left, head_right = st.columns([1, 1.8])

    with head_left:
        st.image("assets/logo.png", width=60)
        st.title("NETFLIX ANALYTICS")
        st.caption("Library Intelligence Hub")

    with head_right:
        st.info(f"**Intelligence Pulse:**\n\n{insight_text}")

    # Preserve state for static charts (Genre Composition)
    base_filtered_df = filtered_df.copy()

    # --- Row 1: Header Slicer (Genre Pills Master) ---
    st.write("") # Spacer
    pill_col = st.columns([1, 4, 1])[1]
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
        st.subheader("Library Overview")
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
            
            st.subheader("Acquisition Trend")
            with st.container(border=True):
                fig_trend = px.area(
                    trend_df, x='Year', y='Titles Added', line_shape='spline',
                    color_discrete_sequence=[NETFLIX_RED]
                )
                fig_trend.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                    xaxis=dict(title=None, gridcolor='#333'), yaxis=dict(title=None, gridcolor='#333'),
                    margin=dict(t=5, b=25, l=10, r=10), height=115
                )
                fig_trend.update_traces(fillcolor='rgba(229, 9, 20, 0.3)', hovertemplate="<b>Year: %{x}</b><br>Titles: %{y}<extra></extra>")
                st.plotly_chart(fig_trend, use_container_width=True, key="trend_chart")

    with col_sun:
        # Sunburst uses base_filtered_df (ignores genre pills)
        sun_df = base_filtered_df[['type', 'listed_in']].explode('listed_in')
        top_type_genres = sun_df.groupby(['type', 'listed_in']).size().reset_index(name='count')
        top_type_genres = top_type_genres.sort_values(['type', 'count'], ascending=[True, False])
        top_type_genres = top_type_genres.groupby('type').head(5).reset_index(drop=True)

        st.subheader("Genre Split")
        with st.container(border=True):
            fig_sun = px.sunburst(
                top_type_genres, path=['type', 'listed_in'], values='count', color='type',
                color_discrete_map={'MOVIE': NETFLIX_RED, 'SHOW': "#444444", 'Movie': NETFLIX_RED, 'TV Show': "#444444"}
            )
            fig_sun.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                margin=dict(t=0, b=0, l=0, r=0), height=115
            )
            fig_sun.update_traces(hovertemplate="<b>%{label}</b><br>Titles: %{value}<extra></extra>")
            st.plotly_chart(fig_sun, use_container_width=True, key="sun_chart")

    # --- Row 2: Cast, Actors & Directors (Talent Hub) ---
    col_cast, col_act, col_dir = st.columns(3)
    
    # Pre-calculate Top Cast
    filtered_ids = filtered_df['id'].unique()
    cast_counts = credits_df[(credits_df['id'].isin(filtered_ids)) & (credits_df['role'] == 'ACTOR')]
    cast_counts = cast_counts['name'].value_counts().head(5).reset_index()
    cast_counts.columns = ['Actor', 'Count']

    with col_cast:
        if not cast_counts.empty:
            st.subheader("Top Cast")
            with st.container(border=True):
                fig_cast = px.bar(
                    cast_counts, x='Count', y='Actor', orientation='h',
                    color_discrete_sequence=[NETFLIX_RED]
                )
                fig_cast.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                    xaxis=dict(title=None, gridcolor='#333'), yaxis=dict(title=None, gridcolor='#333', tickfont=dict(size=10), categoryorder='total ascending'),
                    margin=dict(t=5, b=25, l=10, r=10), height=130
                )
                fig_cast.update_traces(hovertemplate="<b>%{y}</b><br>Titles: %{x}<extra></extra>")
                st.plotly_chart(fig_cast, use_container_width=True, config={'displayModeBar': False}, key="cast_chart")

    with col_act:
        if not filtered_df.empty and not credits_df.empty:
            titles_lite = filtered_df[['id', 'imdb_score']]
            actors_lite = credits_df[credits_df['role'] == 'ACTOR'][['id', 'name']]
            merged_act = pd.merge(actors_lite, titles_lite, on='id')
            act_stats = merged_act.groupby('name').agg({'id': 'count', 'imdb_score': 'mean'}).reset_index()
            act_stats.columns = ['Actor', 'Titles', 'Score']
            top_actors = act_stats.sort_values(['Score', 'Titles'], ascending=False).head(5)
            
            if not top_actors.empty:
                st.subheader("Top Actors")
                with st.container(border=True):
                    fig_act = px.bar(
                        top_actors, x='Score', y='Actor', orientation='h',
                        color='Score', color_continuous_scale=[[0, "#444"], [1, NETFLIX_RED]]
                    )
                    fig_act.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                        xaxis=dict(title=None, gridcolor='#333', range=[0, 10]), yaxis=dict(title=None, gridcolor='#333', categoryorder='total ascending'),
                        margin=dict(t=5, b=25, l=10, r=10), height=130, coloraxis_showscale=False
                    )
                    fig_act.update_traces(hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>", marker_line_width=0)
                    st.plotly_chart(fig_act, use_container_width=True, config={'displayModeBar': False}, key="actor_chart")

    with col_dir:
        if not filtered_df.empty and not credits_df.empty:
            titles_lite = filtered_df[['id', 'imdb_score']]
            dir_lite = credits_df[credits_df['role'] == 'DIRECTOR'][['id', 'name']]
            merged_dir = pd.merge(dir_lite, titles_lite, on='id')
            dir_stats = merged_dir.groupby('name').agg({'id': 'count', 'imdb_score': 'mean'}).reset_index()
            dir_stats.columns = ['Director', 'Titles', 'Score']
            top_dirs = dir_stats.sort_values(['Score', 'Titles'], ascending=False).head(5)
            
            if not top_dirs.empty:
                st.subheader("Top Directors")
                with st.container(border=True):
                    fig_dir = px.bar(
                        top_dirs, x='Score', y='Director', orientation='h',
                        color='Score', color_continuous_scale=[[0, "#444"], [1, NETFLIX_RED]]
                    )
                    fig_dir.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                        xaxis=dict(title=None, gridcolor='#333', range=[0, 10]),
                        yaxis=dict(title=None, gridcolor='#333', categoryorder='total ascending'),
                        margin=dict(t=5, b=25, l=10, r=10), height=130, coloraxis_showscale=False
                    )
                    fig_dir.update_traces(hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>", marker_line_width=0)
                    st.plotly_chart(fig_dir, use_container_width=True, config={'displayModeBar': False}, key="director_chart")

    # --- Row 3: Maturity & Geography (2 Columns) ---
    col_mat_row3, col_geo = st.columns(2)
    
    with col_mat_row3:
        if 'age_certification' in filtered_df.columns:
            rating_counts = filtered_df['age_certification'].value_counts().reset_index()
            rating_counts.columns = ['Rating', 'Count']
            
            st.subheader("Maturity Profile")
            with st.container(border=True):
                fig_rating = px.bar(
                    rating_counts, x='Rating', y='Count',
                    color_discrete_sequence=[NETFLIX_RED]
                )
                fig_rating.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                    xaxis=dict(title=None, gridcolor='#333'), yaxis=dict(title=None, gridcolor='#333'),
                    margin=dict(t=5, b=25, l=10, r=10), height=120
                )
                fig_rating.update_traces(hovertemplate="<b>Rating: %{x}</b><br>Titles: %{y}<extra></extra>")
                st.plotly_chart(fig_rating, use_container_width=True, config={'displayModeBar': False}, key="rating_chart")

    with col_geo:
        if 'country' in filtered_df.columns:
            countries_series = filtered_df['country'].explode().dropna()
            country_counts = countries_series.value_counts().head(5).reset_index()
            country_counts.columns = ['Country', 'Count']
            
            st.subheader("Regional Presence")
            with st.container(border=True):
                fig_country = px.bar(
                    country_counts, x='Count', y='Country', orientation='h',
                    color_discrete_sequence=[NETFLIX_RED]
                )
                fig_country.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                    xaxis=dict(title=None, gridcolor='#333'), yaxis=dict(title=None, gridcolor='#333', tickfont=dict(size=10), categoryorder='total ascending'),
                    margin=dict(t=5, b=25, l=60, r=10), height=120
                )
                fig_country.update_traces(hovertemplate="<b>%{y}</b><br>Titles: %{x}<extra></extra>")
                st.plotly_chart(fig_country, use_container_width=True, key="country_chart")

    # Library Intelligence engine is now integrated into the header

    # Conditional Data Explorer
    if st.session_state.get('show_explorer', False):
        st.markdown("---")
        available_cols = [c for c in ['title', 'type', 'release_year', 'country', 'listed_in'] if c in filtered_df.columns]
        st.dataframe(filtered_df[available_cols].head(50), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Dashboard Error: {e}")
