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

    # --- Sidebar Refinement & Intelligence Hub ---
    with st.sidebar:
        st.divider()
        st.info(f"**Intelligence Pulse:**\n\n{insight_text}")
        st.caption("Deep Engine Analysis • Real-time")

    # --- Header Section (Ultra-Compact Branding) ---
    h_col1, h_col2 = st.columns([1, 8])
    with h_col1: st.image("assets/logo.png", width=35)
    with h_col2: st.caption("NETFLIX ANALYTICS • Library Intelligence Hub")

    # Preserve state for static charts (Genre Composition)
    base_filtered_df = filtered_df.copy()

    # --- Row 1: Header Slicer (Genre Pills Master) ---
    pill_col = st.columns([1, 6, 1])[1]
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

    # --- Row 1: Metrics, Trend & Genre Split (3 Symmetric Columns) ---
    m_count = len(filtered_df[filtered_df['type'].str.upper().str.contains('MOVIE', na=False)])
    tv_count = len(filtered_df[filtered_df['type'].str.upper().str.contains('SHOW', na=False)])
    ratio = round(m_count / tv_count, 1) if tv_count > 0 else "N/A"
    
    col_kpi, col_trend, col_sun = st.columns([1, 1.1, 1])
    
    with col_kpi:
        with st.container(border=True):
            st.markdown("**Overview**")
            k_metrics, k_donut = st.columns([1, 1.2])
            with k_metrics:
                st.metric("Total", f"{len(filtered_df):,}")
                st.metric("Movie", f"{m_count:,}")
                st.metric("Show", f"{tv_count:,}")
            with k_donut:
                ratio_df = pd.DataFrame({"Type": ["Movies", "Shows"], "Count": [m_count, tv_count]})
                fig_ratio = px.pie(ratio_df, values='Count', names='Type', hole=0.7,
                                   color_discrete_map={"Movies": NETFLIX_RED, "Shows": "#444"})
                fig_ratio.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=5, b=5, l=5, r=5), height=105)
                fig_ratio.update_traces(textinfo='none')
                st.plotly_chart(fig_ratio, use_container_width=True, key="ratio_donut", config={'displayModeBar': False})
                st.caption(f"Ratio {ratio}:1")

    with col_trend:
        if 'year_added' in filtered_df.columns:
            trend_df = filtered_df.groupby('year_added').size().reset_index(name='count')
            with st.container(border=True):
                st.markdown("**Acquisition**")
                fig_trend = px.area(trend_df, x='year_added', y='count', line_shape='spline', color_discrete_sequence=[NETFLIX_RED])
                fig_trend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE, size=8),
                    xaxis=dict(title=None, gridcolor='#333'), yaxis=dict(title=None, gridcolor='#333'),
                    margin=dict(t=10, b=30, l=10, r=10), height=110)
                st.plotly_chart(fig_trend, use_container_width=True, key="trend_chart", config={'displayModeBar': False})

    with col_sun:
        with st.container(border=True):
            st.markdown("**Composition**")
            sun_df = base_filtered_df[['type', 'listed_in']].explode('listed_in')
            top_genres = sun_df.groupby('listed_in').size().reset_index(name='count').sort_values('count', ascending=False).head(8)
            fig_tree = px.treemap(top_genres, path=[px.Constant("All"), 'listed_in'], values='count',
                                 color='count', color_continuous_scale=[[0, "#444"], [1, NETFLIX_RED]])
            fig_tree.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                margin=dict(t=10, b=10, l=10, r=10), height=110, coloraxis_showscale=False)
            fig_tree.update_traces(textinfo="label+value")
            st.plotly_chart(fig_tree, use_container_width=True, key="tree_chart", config={'displayModeBar': False})

    # --- Row 2: Deep Analysis (5 Ultra-Compact Columns) ---
    c1, c2, c3, c4, c5 = st.columns(5)
    
    # Data prep
    filtered_ids = filtered_df['id'].unique()
    credits_filter = credits_df[credits_df['id'].isin(filtered_ids)]
    
    with c1:
        with st.container(border=True):
            st.write("**Cast**")
            cast = credits_filter[credits_filter['role'] == 'ACTOR']['name'].value_counts().head(5).reset_index()
            fig_cast = px.bar(cast, x='count', y='name', orientation='h', 
                             color='count', color_continuous_scale=[[0, "#444"], [1, NETFLIX_RED]])
            fig_cast.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                xaxis=dict(visible=False), yaxis=dict(title=None, categoryorder='total ascending', tickfont=dict(size=8)),
                margin=dict(t=5, b=25, l=10, r=10), height=110, coloraxis_showscale=False)
            st.plotly_chart(fig_cast, use_container_width=True, config={'displayModeBar': False}, key="c1")

    with c2:
        with st.container(border=True):
            st.write("**Actors**")
            act_perf = credits_filter[credits_filter['role'] == 'ACTOR'].merge(filtered_df[['id', 'imdb_score']], on='id').groupby('name')['imdb_score'].mean().reset_index().sort_values('imdb_score', ascending=False).head(5)
            fig_act = px.bar(act_perf, x='imdb_score', y='name', orientation='h', 
                            color='imdb_score', color_continuous_scale=[[0, "#444"], [1, NETFLIX_RED]])
            fig_act.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                xaxis=dict(visible=False, range=[0, 10]), yaxis=dict(title=None, categoryorder='total ascending', tickfont=dict(size=8)),
                margin=dict(t=5, b=25, l=10, r=10), height=110, coloraxis_showscale=False)
            st.plotly_chart(fig_act, use_container_width=True, config={'displayModeBar': False}, key="c2")

    with c3:
        with st.container(border=True):
            st.write("**Directors**")
            dir_perf = credits_filter[credits_filter['role'] == 'DIRECTOR'].merge(filtered_df[['id', 'imdb_score']], on='id').groupby('name')['imdb_score'].mean().reset_index().sort_values('imdb_score', ascending=False).head(5)
            fig_dir = px.bar(dir_perf, x='imdb_score', y='name', orientation='h', 
                            color='imdb_score', color_continuous_scale=[[0, "#444"], [1, NETFLIX_RED]])
            fig_dir.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                xaxis=dict(visible=False, range=[0, 10]), yaxis=dict(title=None, categoryorder='total ascending', tickfont=dict(size=8)),
                margin=dict(t=5, b=25, l=10, r=10), height=110, coloraxis_showscale=False)
            st.plotly_chart(fig_dir, use_container_width=True, config={'displayModeBar': False}, key="c3")

    with c4:
        with st.container(border=True):
            st.write("**Maturity**")
            ratings = filtered_df['age_certification'].value_counts().head(5).reset_index()
            fig_rat = px.bar(ratings, x='age_certification', y='count', 
                            color='count', color_continuous_scale=[[0, "#444"], [1, NETFLIX_RED]])
            fig_rat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                xaxis=dict(title=None, tickfont=dict(size=8), tickangle=-45), yaxis=dict(visible=False),
                margin=dict(t=5, b=45, l=10, r=10), height=110, coloraxis_showscale=False)
            st.plotly_chart(fig_rat, use_container_width=True, config={'displayModeBar': False}, key="c4")

    with c5:
        with st.container(border=True):
            st.write("**Region**")
            geo = filtered_df['country'].explode().value_counts().head(5).reset_index()
            fig_geo = px.bar(geo, x='count', y='country', orientation='h', color_discrete_sequence=[NETFLIX_RED])
            fig_geo.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=WHITE),
                xaxis=dict(visible=False), yaxis=dict(title=None, categoryorder='total ascending', tickfont=dict(size=8)),
                margin=dict(t=5, b=25, l=10, r=10), height=110)
            st.plotly_chart(fig_geo, use_container_width=True, key="c5", config={'displayModeBar': False})

    if st.session_state.get('show_explorer', False):
        st.dataframe(filtered_df[['title', 'type', 'release_year', 'imdb_score']].head(10), use_container_width=True)

except Exception as e:
    st.error(f"Dashboard Error: {e}")
