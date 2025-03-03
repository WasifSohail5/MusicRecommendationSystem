import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from fuzzywuzzy import process  # For improved search functionality

# Set Page Configuration
st.set_page_config(
    page_title="AMUSIC - Music Recommendation System",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/WasifSohail5',
        'Report a bug': "https://github.com/WasifSohail5/MusicRecommendationSystem/issues",
        'About': "# AI-Powered Music Recommendation System"
    }
)

# Custom CSS for Enhanced UI
st.markdown("""
    <style>
    .stApp {
        background-color: #0F1116;
        color: #FFFFFF;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6366F1, #8B5CF6);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75em 1.5em;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    .stTextInput>div>input {
        background-color: #1F2937;
        color: #FFFFFF;
        border-radius: 8px;
        padding: 0.75em;
    }
    .stSelectbox>div>div {
        background-color: #1F2937;
        color: #FFFFFF;
        border-radius: 8px;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(195deg, #1A1C23, #14161B);
        border-right: 1px solid #2D3748;
        padding: 20px;
    }
    .card {
        background: #1F2937;
        padding: 1.5em;
        border-radius: 16px;
        margin-bottom: 1em;
        border: 1px solid #2D3748;
        transition: all 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        border-color: #4F46E5;
    }
    .feature-badge {
        background: rgba(79, 70, 229, 0.2);
        color: #818CF8;
        padding: 0.3em 0.8em;
        border-radius: 20px;
        font-size: 0.9em;
        margin: 0.3em;
    }
    .hover-glow:hover {
        filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.3));
    }
    </style>
""", unsafe_allow_html=True)

# Get the current directory
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()

logo_path = current_dir / "logo.png"
logo_exists = logo_path.exists()
# Load Data Function with enhanced caching
@st.cache_data(show_spinner=False)
def load_data():
    try:
        data_path = current_dir / "data" / "data.csv"
        return pd.read_csv(data_path, encoding='utf-8')
    except Exception as e:
        st.error(f"Error loading datasets: {e}")
        return None


# Load Models Function with version check
@st.cache_resource(show_spinner=False)
def load_models():
    try:
        model_path = current_dir / "data_model.pkl"
        return joblib.load(model_path)
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None


# Initialize Session State
session_defaults = {
    "favorites": [],
    "playlist": [],
    "recent_searches": []
}
for key, value in session_defaults.items():
    st.session_state.setdefault(key, value)

# Load Data and Models
data = load_data()
model = load_models()

# Sidebar UI with enhanced styling
with st.sidebar:
    # Display Logo at the Top
    if logo_exists:
        st.image(str(logo_path), use_container_width=True)
    else:
        st.warning("Logo image not found. Please ensure 'logo.png' is in the correct directory.")

    st.markdown("""
        <div style="text-align: center; margin-bottom: 2em;">
            <p style="color: #94A3B8; margin-top: 0.5em;">AI-Powered Music Discovery</p>
        </div>
    """, unsafe_allow_html=True)

    with st.expander("🚀 Quick Access", expanded=True):
        selected_tab = st.radio("Navigation", [
            "🏠 Home",
            "🎵 Recommendations",
            "🔍 Advanced Search",
            "📊 Music Insights",
            "❤️ Favorites",
            "🎶 Smart Playlist"
        ], index=0)

    with st.expander("🔧 User Settings"):
        st.checkbox("Enable Explicit Content", False, help="Filter explicit content")
        st.checkbox("High Quality Streaming", True)
        st.slider("Volume", 0, 100, 75)

    st.markdown("""
        <div style="margin-top: 2em; padding: 1em; background: #1F2937; border-radius: 12px;">
            <p style="margin: 0; color: #94A3B8;">🎧 Now Playing</p>
            <p style="margin: 0.5em 0; font-weight: bold;">Nothing playing</p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <button style="background: none; border: none; color: #6366F1; cursor: pointer;">▶️ Play</button>
                <div style="display: flex; gap: 0.5em;">
                    <span style="color: #94A3B8;">🔊 75%</span>
                    <span style="color: #94A3B8;">⏳ 0:00 / 3:45</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
# Initialize Session State
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "playlist" not in st.session_state:
    st.session_state.playlist = []
if "message" not in st.session_state:
    st.session_state.message = None  # Initialize the message variable
# Enhanced Home Tab
if "Home" in selected_tab:
    col1, col2 = st.columns([2, 3])
    with col1:
        st.markdown("""
            <div style="margin-bottom: 2em;">
                <h1 style="color: #6366F1;">Discover Your Sound</h1>
                <p style="color: #94A3B8; font-size: 1.1em;">
                    AMUSIC uses advanced machine learning to analyze your music preferences 
                    and deliver personalized recommendations. Explore new genres, rediscover 
                    classics, and create perfect playlists.
                </p>
            </div>
        """, unsafe_allow_html=True)

        if data is not None:
            st.markdown("### 🚀 Quick Actions")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎵 Explore New Releases", help="Discover recently added songs"):
                    st.session_state.selected_tab = "Advanced Search"
            with col2:
                if st.button("📊 View Trends", help="See current music trends"):
                    st.session_state.selected_tab = "Music Insights"

    with col2:
        if data is not None:
            st.markdown("### 📈 Music Trends Overview")
            try:
                trend_data = data.groupby('year').agg({
                    'popularity': 'mean',
                    'danceability': 'mean',
                    'energy': 'mean'
                }).reset_index()

                fig = px.line(trend_data, x='year', y=['popularity', 'danceability', 'energy'],
                              labels={'value': 'Score', 'variable': 'Metric'},
                              color_discrete_map={
                                  'popularity': '#6366F1',
                                  'danceability': '#10B981',
                                  'energy': '#EF4444'
                              })
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    legend_title_text='Metrics'
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Couldn't generate trend chart: {e}")

# Enhanced Recommendations Tab with multi-factor filtering
import time  # Add this import at the top of your script

# Initialize Session State
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "playlist" not in st.session_state:
    st.session_state.playlist = []
if "message" not in st.session_state:
    st.session_state.message = None

# Callback function for adding to favorites
def add_to_favorites(song_name):
    if song_name not in st.session_state.favorites:
        st.session_state.favorites.append(song_name)
        st.session_state.message = f"Added **{song_name}** to Favorites!"
    else:
        st.session_state.message = f"**{song_name}** is already in your Favorites!"

# Callback function for adding to playlist
def add_to_playlist(song_name):
    if song_name not in st.session_state.playlist:
        st.session_state.playlist.append(song_name)
        st.session_state.message = f"Added **{song_name}** to Playlist!"
    else:
        st.session_state.message = f"**{song_name}** is already in your Playlist!"

if "Recommendations" in selected_tab:
    st.markdown("## 🎯 Smart Recommendations")
    if data is not None and model is not None:
        with st.expander("⚙️ Recommendation Settings", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                song_name = st.selectbox("Seed Song", data["name"].unique())
            with col2:
                top_n = st.slider("Number of Recommendations", 5, 20, 10)
            with col3:
                diversity = st.slider("Diversity", 0.0, 1.0, 0.7,
                                      help="Balance between similarity and variety")

        if st.button("Generate Recommendations", key="rec_gen"):
            with st.spinner("🎧 Analyzing your music taste..."):
                try:
                    # Find the index of the selected song
                    idx = data.index[data["name"] == song_name].tolist()[0]

                    # Ensure the query point has valid feature names
                    query_point = data.loc[idx, model.feature_names_in_].values.reshape(1, -1)
                    query_point = pd.DataFrame(query_point, columns=model.feature_names_in_)  # Add feature names

                    # Get recommendations
                    distances, indices = model.kneighbors(query_point, n_neighbors=top_n * 2)

                    # Apply diversity filtering
                    rec_indices = [indices[0][0]]
                    for i in indices[0][1:]:
                        if len(rec_indices) >= top_n:
                            break
                        if data.iloc[i]['name'] != song_name:
                            rec_indices.append(i)

                    recommendations = data.iloc[rec_indices[:top_n]]

                    # Display recommendations with audio features
                    st.markdown(f"### 🎧 Recommendations based on *{song_name}*")
                    for _, row in recommendations.iterrows():
                        with st.container():
                            col1, col2, col3 = st.columns([1, 4, 2])
                            with col1:
                                st.markdown(f"<div class='hover-glow' style='font-size: 3em;'>🎵</div>",
                                            unsafe_allow_html=True)
                            with col2:
                                st.markdown(f"""
                                    <div class="card">
                                        <h4>{row['name']}</h4>
                                        <p style="color: #94A3B8;">{row['artists']}</p>
                                        <div style="display: flex; flex-wrap: wrap;">
                                            <span class="feature-badge">🎶 {row['tempo']:.0f} BPM</span>
                                            <span class="feature-badge">💃 {row['danceability'] * 100:.0f}% Dance</span>
                                            <span class="feature-badge">🔥 {row['energy'] * 100:.0f}% Energy</span>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                            with col3:
                                # Add to Favorites and Playlist buttons
                                if st.button("❤️ Add to Favorites", key=f"fav_{row['id']}", on_click=add_to_favorites, args=(row['name'],)):
                                    pass  # The callback function handles the logic

                                if st.button("➕ Add to Playlist", key=f"add_{row['id']}", on_click=add_to_playlist, args=(row['name'],)):
                                    pass  # The callback function handles the logic
                except Exception as e:
                    st.error(f"Recommendation error: {str(e)}")

    # Display the message at the top of the page
    if st.session_state.message:
        st.success(st.session_state.message)
        st.session_state.message = None  # Clear the message after displaying

# Enhanced Search with fuzzy matching
if "Advanced Search" in selected_tab:
    st.markdown("## 🔍 Advanced Music Search")
    if data is not None:
        # Search Bar
        search_query = st.text_input("Search for a song or artist", placeholder="Enter song name or artist")

        # Basic Filters
        with st.expander("🎛️ Filters", expanded=True):
            # Year Filter (if 'year' column exists)
            if 'year' in data.columns:
                year_range = st.slider(
                    "Release Year",
                    min_value=int(data['year'].min()),
                    max_value=int(data['year'].max()),
                    value=(2000, 2020)
                )
            else:
                st.warning("Year information not available in the dataset.")
                year_range = (2000, 2020)  # Default values

            # Tempo Filter (if 'tempo' column exists)
            if 'tempo' in data.columns:
                bpm_range = st.slider(
                    "Tempo (BPM)",
                    min_value=int(data['tempo'].min()),
                    max_value=int(data['tempo'].max()),
                    value=(80, 120)
                )
            else:
                st.warning("Tempo information not available in the dataset.")
                bpm_range = (80, 120)  # Default values

        # Apply Filters
        if search_query:
            # Fuzzy matching for better search
            choices = data['name'] + " - " + data['artists']
            matches = process.extract(search_query, choices, limit=20)
            matched_indices = [match[2] for match in matches if match[1] > 60]  # Extract indices from matches
            search_results = data.iloc[matched_indices]
        else:
            search_results = data

        # Apply year and tempo filters (if columns exist)
        if 'year' in data.columns:
            search_results = search_results[search_results['year'].between(*year_range)]
        if 'tempo' in data.columns:
            search_results = search_results[search_results['tempo'].between(*bpm_range)]

        # Display Results
        if not search_results.empty:
            st.markdown(f"### 🎵 Found {len(search_results)} songs")

            # Limit the number of results displayed initially
            num_results_to_show = min(10, len(search_results))
            st.markdown(f"Showing **{num_results_to_show}** results. Use the search bar to refine your results.")

            for _, row in search_results.head(num_results_to_show).iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([1, 4, 2])
                    with col1:
                        st.markdown(f"<div class='hover-glow' style='font-size: 2em;'>🎵</div>",
                                    unsafe_allow_html=True)
                    with col2:
                        # Display song details
                        st.markdown(f"""
                            <div class="card">
                                <h4>{row['name']}</h4>
                                <p style="color: #94A3B8;">
                                    {row['artists']} • {row['year'] if 'year' in data.columns else 'N/A'}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        if st.button("➕ Add to Playlist", key=f"add_{row['id']}"):
                            st.session_state.playlist.append(row['name'])
                            st.success(f"Added **{row['name']}** to playlist!")

            # Show a "Load More" button if there are more results
            if len(search_results) > num_results_to_show:
                if st.button("Load More Results"):
                    num_results_to_show = min(num_results_to_show + 10, len(search_results))
                    st.rerun()
        else:
            st.warning("No matching songs found. Try adjusting your search or filters.")
# Enhanced Visualizations Tab
if "Music Insights" in selected_tab:
    st.markdown("## 📊 Advanced Music Analytics")
    if data is not None:
        # Define visualization options based on available columns
        viz_options = {}

        # Add Genre Distribution only if 'genre' column exists
        if 'genre' in data.columns:
            viz_options["Genre Distribution"] = "bar-chart"

        # Add other visualizations
        viz_options.update({
            "Audio Features Radar": "radar",
            "Song Duration Analysis": "clock",
            "Popularity Correlation": "heatmap",
            "Feature Distribution": "histogram",  # New visualization
            "Feature Comparison": "scatter"  # New visualization
        })

        # Let the user choose a visualization
        viz_choice = st.selectbox(
            "Choose Visualization",
            list(viz_options.keys()),
            format_func=lambda x: f"{viz_options[x]} {x}"
        )

        # Genre Distribution (only if 'genre' column exists)
        if viz_choice == "Genre Distribution" and 'genre' in data.columns:
            genre_counts = data['genre'].value_counts().nlargest(15)
            fig = px.bar(
                genre_counts,
                orientation='h',
                color=genre_counts.values,
                color_continuous_scale='Bluered',
                title="Top Genres by Song Count"
            )
            fig.update_layout(
                xaxis_title="Number of Songs",
                yaxis_title="Genre",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

        # Audio Features Radar
        elif viz_choice == "Audio Features Radar":
            features = ['danceability', 'energy', 'acousticness',
                        'instrumentalness', 'liveness', 'valence']

            # Check if all required features exist in the dataset
            missing_features = [f for f in features if f not in data.columns]
            if missing_features:
                st.warning(f"Missing features: {', '.join(missing_features)}. Cannot generate radar chart.")
            else:
                avg_features = data[features].mean()
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=avg_features.values,
                    theta=avg_features.index,
                    fill='toself',
                    name='Average Features'
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True)),
                    showlegend=False,
                    title="Average Audio Features"
                )
                st.plotly_chart(fig, use_container_width=True)

        # Song Duration Analysis
        elif viz_choice == "Song Duration Analysis":
            if 'duration_ms' in data.columns:
                data['duration_min'] = data['duration_ms'] / 60000
                fig = px.histogram(
                    data,
                    x='duration_min',
                    nbins=50,
                    title="Song Duration Distribution",
                    labels={'duration_min': 'Duration (minutes)'}
                )
                fig.update_layout(
                    xaxis_title="Duration (minutes)",
                    yaxis_title="Number of Songs",
                    bargap=0.1
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("'duration_ms' column not found in the dataset. Cannot generate duration analysis.")

        # Popularity Correlation
        elif viz_choice == "Popularity Correlation":
            if 'popularity' in data.columns:
                numeric_cols = data.select_dtypes(include='number').columns.tolist()
                selected_features = st.multiselect(
                    "Select Features",
                    numeric_cols,
                    default=['danceability', 'energy', 'loudness']
                )

                if selected_features:
                    corr_matrix = data[selected_features + ['popularity']].corr()
                    fig = px.imshow(
                        corr_matrix,
                        text_auto=True,
                        color_continuous_scale='RdBu',
                        title="Feature Correlation Matrix"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("'popularity' column not found in the dataset. Cannot generate correlation heatmap.")

        # Feature Distribution (New Visualization)
        elif viz_choice == "Feature Distribution":
            # Select a feature to visualize
            feature = st.selectbox(
                "Select Feature",
                ['danceability', 'energy', 'acousticness', 'valence', 'tempo', 'loudness']
            )

            if feature in data.columns:
                fig = px.histogram(
                    data,
                    x=feature,
                    nbins=50,
                    title=f"Distribution of {feature.capitalize()}",
                    labels={feature: feature.capitalize()}
                )
                fig.update_layout(
                    xaxis_title=feature.capitalize(),
                    yaxis_title="Number of Songs",
                    bargap=0.1
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"'{feature}' column not found in the dataset.")

        # Feature Comparison (New Visualization)
        elif viz_choice == "Feature Comparison":
            col1, col2 = st.columns(2)
            with col1:
                x_feature = st.selectbox(
                    "X-axis Feature",
                    ['danceability', 'energy', 'acousticness', 'valence', 'tempo', 'loudness']
                )
            with col2:
                y_feature = st.selectbox(
                    "Y-axis Feature",
                    ['danceability', 'energy', 'acousticness', 'valence', 'tempo', 'loudness']
                )

            if x_feature in data.columns and y_feature in data.columns:
                fig = px.scatter(
                    data,
                    x=x_feature,
                    y=y_feature,
                    title=f"{x_feature.capitalize()} vs {y_feature.capitalize()}",
                    labels={
                        x_feature: x_feature.capitalize(),
                        y_feature: y_feature.capitalize()
                    }
                )
                fig.update_layout(
                    xaxis_title=x_feature.capitalize(),
                    yaxis_title=y_feature.capitalize()
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"Required columns not found in the dataset.")

# Favorites Tab
elif "Favorites" in selected_tab:
    st.subheader("❤️ Your Favorites")
    if st.session_state.favorites:
        for i, song in enumerate(st.session_state.favorites):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"<div class='card'>🎵 {song}</div>", unsafe_allow_html=True)
            with col2:
                if st.button("Remove", key=f"remove_fav_{i}"):
                    st.session_state.favorites.remove(song)
                    st.rerun()

        if st.button("Export Favorites"):
            try:
                pd.DataFrame(st.session_state.favorites, columns=["Song"]).to_csv("favorites.csv", index=False)
                st.success("Favorites exported as favorites.csv!")
                st.download_button(
                    label="Download CSV",
                    data=pd.DataFrame(st.session_state.favorites, columns=["Song"]).to_csv(index=False).encode('utf-8'),
                    file_name="favorites.csv",
                    mime="text/csv",
                )
            except Exception as e:
                st.error(f"Error exporting favorites: {e}")
    else:
        st.info("No favorites yet! Go to Search or Recommendations to add some songs.")

# Playlist Tab
elif "Playlist" in selected_tab:
    st.subheader("🎶 Your Playlist")
    if st.session_state.playlist:
        for i, song in enumerate(st.session_state.playlist):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"<div class='card'>🎵 {song}</div>", unsafe_allow_html=True)
            with col2:
                if st.button("Remove", key=f"remove_playlist_{i}"):
                    st.session_state.playlist.remove(song)
                    st.rerun()

        if st.button("Export Playlist"):
            try:
                pd.DataFrame(st.session_state.playlist, columns=["Song"]).to_csv("playlist.csv", index=False)
                st.success("Playlist exported as playlist.csv!")
                st.download_button(
                    label="Download CSV",
                    data=pd.DataFrame(st.session_state.playlist, columns=["Song"]).to_csv(index=False).encode('utf-8'),
                    file_name="playlist.csv",
                    mime="text/csv",
                )
            except Exception as e:
                st.error(f"Error exporting playlist: {e}")
    else:
        st.info("Your playlist is empty! Go to Search or Recommendations to add songs.")
