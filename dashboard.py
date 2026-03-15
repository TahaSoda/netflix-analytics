import streamlit as st
import pandas as pd
import plotly.express as px
import os
import ast

# --- Page Config ---
st.set_page_config(
    page_title="Netflix Analytics | Insights Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- Constants ---
NETFLIX_RED = "#E50914"
WHITE = "#FFFFFF"

# --- Helper Functions ---
def parse_list_col(val):
    try:
        if isinstance(val, str) and val.startswith('['):
            return ast.literal_eval(val)
        return val
    except:
        return val

@st.cache_data
def load_data():
    # Load data from local CSVs
    titles_df = pd.read_csv("titles.csv") if os.path.exists("titles.csv") else pd.DataFrame()
    credits_df = pd.read_csv("credits.csv") if os.path.exists("credits.csv") else pd.DataFrame()
    
    if titles_df.empty:
        return pd.DataFrame(), pd.DataFrame()
        
    column_mapping = {'production_countries': 'country', 'genres': 'listed_in'}
    titles_df = titles_df.rename(columns=column_mapping)
    
    if 'date_added' in titles_df.columns:
        titles_df['date_added'] = pd.to_datetime(titles_df['date_added'].str.strip(), format='%B %d, %Y', errors='coerce')
        titles_df['year_added'] = titles_df['date_added'].dt.year
    else:
        titles_df['year_added'] = titles_df['release_year']
        
    for col in ['country', 'listed_in']:
        if col in titles_df.columns:
            titles_df[col] = titles_df[col].apply(parse_list_col)
            
    if not credits_df.empty and 'id' in credits_df.columns:
        credits_df = credits_df.set_index('id')
            
    return titles_df, credits_df

@st.cache_data
def get_filter_options(df):
    genres = sorted(list(df['listed_in'].explode().dropna().unique()))
    countries = sorted(list(df['country'].explode().dropna().unique()))
    return genres, countries

# --- Main App Logic ---
try:
    df, credits_df = load_data()
    if df.empty:
        st.error("Dataset 'titles.csv' not found. Please ensure the file is in the same directory.")
        st.stop()

    # --- Sidebar Filters ---
    with st.sidebar:
        st.subheader("Advanced Filters")
        content_types = sorted(df['type'].astype(str).unique())
        content_selection = st.multiselect("Content Type", options=content_types, default=list(content_types))
        
        min_yr, max_yr = int(df['release_year'].min()), int(df['release_year'].max())
        years = st.slider("Release Years", min_value=min_yr, max_value=max_yr, value=(min_yr, max_yr))
        search_query = st.text_input("🔍 Search Titles")
        
        all_genres, all_countries = get_filter_options(df)
        selected_genres = st.multiselect("Filter by Genre", options=all_genres)
        selected_countries = st.multiselect("Filter by Country", options=all_countries)
        
        sort_by = st.selectbox("Sort Library By", options=["Release Year", "Title", "IMDb Score"])
        
        if st.button("Reset All Filters"):
            st.rerun()

    # --- Step 1: Apply Sidebar Filters (Base Data) ---
    base_df = df[
        (df['type'].isin(content_selection)) & 
        (df['release_year'].between(years[0], years[1]))
    ].copy()
    
    if search_query:
        base_df = base_df[base_df['title'].astype(str).str.contains(search_query, case=False, na=False)]
    if selected_genres:
        base_df = base_df[base_df['listed_in'].apply(lambda x: any(g in x for g in selected_genres) if isinstance(x, list) else False)]
    if selected_countries:
        base_df = base_df[base_df['country'].apply(lambda x: any(c in x for c in selected_countries) if isinstance(x, list) else False)]

    # --- Step 2: Extract Clicks from Treemaps (Toggle Logic) ---
    active_genre = "All"
    active_region = "All"

    if "tree_comp" in st.session_state:
        comp_selection = st.session_state["tree_comp"].get("selection", {}).get("points", [])
        if comp_selection:
            active_genre = comp_selection[0].get("label", "All")

    if "tree_region" in st.session_state:
        region_selection = st.session_state["tree_region"].get("selection", {}).get("points", [])
        if region_selection:
            active_region = region_selection[0].get("label", "All")

    # --- Step 3: Apply Treemap Filters to create Final Data ---
    final_df = base_df.copy()
    if active_genre != "All":
        final_df = final_df[final_df['listed_in'].apply(lambda x: active_genre in x if isinstance(x, list) else False)]
    if active_region != "All":
        final_df = final_df[final_df['country'].apply(lambda x: active_region in x if isinstance(x, list) else False)]

    # Final Sort
    sort_map = {"Release Year": "release_year", "Title": "title", "IMDb Score": "imdb_score"}
    if not final_df.empty and sort_map[sort_by] in final_df.columns:
        final_df = final_df.sort_values(by=sort_map[sort_by], ascending=(sort_by == "Title"))

    # --- UI Rendering ---
    # Compact Header Section
    h_col1, h_col2 = st.columns([1, 8], vertical_alignment="center")
    with h_col1:
        if os.path.exists("assets/logo.png"):
            st.image("assets/logo.png", width=70)
    with h_col2:
        st.markdown("## NETFLIX ANALYTICS")
        st.markdown("*Interactive Insights & Library Intelligence Dashboard*")


    # Row 1: Metrics, Trend & Composition
    col_kpi, col_trend, col_sun = st.columns([1, 1.1, 1])
    
    with col_kpi:
        with st.container(border=True):
            st.markdown("**Overview**")
            m_count = len(final_df[final_df['type'].astype(str).str.upper().str.contains('MOVIE', na=False)])
            tv_count = len(final_df[final_df['type'].astype(str).str.upper().str.contains('SHOW', na=False)])
            k1, k2 = st.columns([1, 1.2])
            with k1:
                st.metric("Total", f"{len(final_df):,}")
                st.metric("Movie", f"{m_count:,}")
            with k2:
                if m_count > 0 or tv_count > 0:
                    ratio_df = pd.DataFrame({'label': ['Movies', 'Shows'], 'value': [m_count, tv_count]})
                    fig_ratio = px.pie(ratio_df, values='value', names='label', hole=0.7, color_discrete_sequence=[NETFLIX_RED, '#444'])
                    fig_ratio.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=11)), margin=dict(t=0, b=30, l=0, r=0), height=170, paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_ratio, use_container_width=True, config={'displayModeBar': False})

    with col_trend:
        with st.container(border=True):
            st.markdown("**Acquisition Trend**")
            if 'year_added' in final_df.columns and not final_df.empty:
                trend_df = final_df.groupby('year_added').size().reset_index(name='count')
                fig_trend = px.area(trend_df, x='year_added', y='count', color_discrete_sequence=[NETFLIX_RED])
                fig_trend.update_layout(height=160, margin=dict(t=10, b=0, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title=None, yaxis_title=None)
                st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

    with col_sun:
        with st.container(border=True):
            header_text = f"**Composition** | :red[{active_genre}]" if active_genre != "All" else "**Composition**"
            st.markdown(header_text)
            sun_df = base_df[['type', 'listed_in']].explode('listed_in')
            top_g = sun_df.groupby('listed_in').size().reset_index(name='count').sort_values('count', ascending=False).head(8)
            
            if not top_g.empty:
                fig_tree = px.treemap(top_g, path=[px.Constant("All"), 'listed_in'], values='count', color='count', color_continuous_scale=[[0, "#333"], [1, NETFLIX_RED]])
                fig_tree.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=165, coloraxis_showscale=False)
                st.plotly_chart(fig_tree, use_container_width=True, key="tree_comp", on_select="rerun", selection_mode="points", config={'displayModeBar': False})

    # Row 2: Analysis Suite
    c1, c4, c5 = st.columns([1, 1, 2])
    
    filtered_ids = final_df['id']
    credits_filter = credits_df.loc[credits_df.index.isin(filtered_ids)].reset_index() if not credits_df.empty else pd.DataFrame()

    with c1:
        with st.container(border=True):
            st.write("**Top Cast**")
            if not credits_filter.empty:
                cast_counts = credits_filter[credits_filter['role'] == 'ACTOR']['name'].value_counts().head(8)
                cast = pd.DataFrame({'name': cast_counts.index, 'count': cast_counts.values})
                fig_cast = px.bar(cast, x='count', y='name', orientation='h', color_discrete_sequence=[NETFLIX_RED])
                fig_cast.update_layout(height=200, margin=dict(t=0, b=0, l=0, r=0), xaxis_visible=False, yaxis_title=None, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_cast, use_container_width=True, config={'displayModeBar': False})

    with c4:
        with st.container(border=True):
            st.write("**Maturity**")
            if 'age_certification' in final_df.columns:
                ratings_counts = final_df['age_certification'].value_counts().head(8)
                ratings = pd.DataFrame({'age_certification': ratings_counts.index, 'count': ratings_counts.values})
                fig_mat = px.bar(ratings, x='age_certification', y='count', color_discrete_sequence=[NETFLIX_RED])
                fig_mat.update_layout(height=200, margin=dict(t=10, b=0, l=0, r=0), yaxis_visible=False, xaxis_title=None)
                st.plotly_chart(fig_mat, use_container_width=True, config={'displayModeBar': False})

    with c5:
        with st.container(border=True):
            header_text = f"**Region** | :red[{active_region}]" if active_region != "All" else "**Region**"
            st.markdown(header_text)
            if 'country' in base_df.columns:
                geo_counts = base_df['country'].explode().value_counts().head(8)
                geo = pd.DataFrame({'country': geo_counts.index, 'count': geo_counts.values})
                if not geo.empty:
                    fig_geo = px.treemap(geo, path=[px.Constant("All"), 'country'], values='count', color='count', color_continuous_scale=[[0, "#333"], [1, NETFLIX_RED]])
                    fig_geo.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=210, coloraxis_showscale=False)
                    st.plotly_chart(fig_geo, use_container_width=True, key="tree_region", on_select="rerun", selection_mode="points", config={'displayModeBar': False})

except Exception as e:
    st.error(f"Dashboard Error: {e}")