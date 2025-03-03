import streamlit as st
import pandas as pd
import joblib
import os
import plotly.express as px
from pathlib import Path
import random

# Set Page Configuration
st.set_page_config(page_title="MixTune - AI Music Recommender", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Enhanced UI
st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E2F;
        color: #FFFFFF;
    }
    .stButton>button {
        background: linear-gradient(90deg, #FF6F61, #DE4D86);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5em 1em;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
    }
    .stTextInput>div>input {
        background-color: #2D2D44;
        color: #FFFFFF;
        border-radius: 8px;
    }
    .stSelectbox>div>div {
        background-color: #2D2D44;
        color: #FFFFFF;
        border-radius: 8px;
    }
    .stSlider>div>div {
        background-color: #FF6F61;
    }
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #3A3A5A, #2D2D44);
        border-radius: 0 10px 10px 0;
        padding: 15px;
    }
    div[data-testid="stSidebar"] .block-container {
        padding-top: 0;
    }
    .sidebar-item {
        background-color: rgba(45, 45, 68, 0.8);
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.2s;
        border-left: 3px solid transparent;
    }
    .sidebar-item:hover {
        background-color: rgba(58, 58, 90, 0.9);
        border-left: 3px solid #FF6F61;
    }
    .sidebar-item.active {
        background-color: rgba(58, 58, 90, 0.9);
        border-left: 3px solid #FF6F61;
    }
    .user-profile {
        background-color: rgba(45, 45, 68, 0.9);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0 20px 0;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .user-avatar {
        width: 40px;
        height: 40px;
        background-color: #DE4D86;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
    }
    .card {
        background-color: #2D2D44;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
        position: relative;
    }
    .card:hover {
        transform: translateY(-5px);
    }
    .song-card {
        background-color: #2D2D44;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
        border-left: 3px solid #FF6F61;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .song-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.2);
    }
    .song-info {
        flex-grow: 1;
    }
    .song-actions {
        display: flex;
        gap: 8px;
    }
    .action-button {
        background-color: rgba(255, 111, 97, 0.15);
        color: #FF6F61;
        border: none;
        border-radius: 50%;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s;
    }
    .action-button:hover {
        background-color: rgba(255, 111, 97, 0.3);
    }
    .page-header {
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid rgba(255, 111, 97, 0.3);
    }
    .loading-bar {
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #FF6F61, #DE4D86);
        position: relative;
        overflow: hidden;
        border-radius: 2px;
    }
    .loading-bar::after {
        content: "";
        position: absolute;
        top: 0;
        left: -50%;
        width: 50%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
        animation: loading 1.5s infinite;
    }
    @keyframes loading {
        0% { left: -50%; }
        100% { left: 150%; }
    }
    </style>
""", unsafe_allow_html=True)

# Get the current directory
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()


# Load Data Function
@st.cache_data
def load_data():
    with st.spinner("🎵 Loading datasets..."):
        try:
            # Use relative paths instead of hardcoded ones
            data_path = current_dir / "data"
            data_file = data_path / "data.csv"

            if not data_file.exists():
                st.error(f"Data file not found: {data_file}")
                return None

            data = pd.read_csv(data_file)
            return data
        except Exception as e:
            st.error(f"Error loading datasets: {e}")
            return None


# Load Models Function
@st.cache_resource
def load_models():
    try:
        # Use relative paths
        model_path = current_dir / "data_model.pkl"

        if not model_path.exists():
            st.warning(f"⚠️ Model file not found: {model_path}")
            return None

        return joblib.load(model_path)
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None


# Initialize Session State
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "playlist" not in st.session_state:
    st.session_state.playlist = []
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "🏠 Home"
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {"name": "Guest", "status": "Free"}
if "total_plays" not in st.session_state:
    st.session_state.total_plays = random.randint(124, 357)
if "history" not in st.session_state:
    st.session_state.history = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True


# Function to add song to favorites
def add_to_favorites(song_name):
    if song_name not in st.session_state.favorites:
        st.session_state.favorites.append(song_name)
        return True
    return False


# Function to add song to playlist
def add_to_playlist(song_name):
    if song_name not in st.session_state.playlist:
        st.session_state.playlist.append(song_name)
        return True
    return False


# Load Data and Models
data = load_data()
model = load_models()

# Logo path handling with error checking
logo_path = current_dir / "logo.png"
logo_exists = logo_path.exists()

# Sidebar UI - Enhanced
with st.sidebar:
    if logo_exists:
        st.image(str(logo_path), use_container_width=True)
    else:
        # Fallback text logo if image is missing
        st.markdown("""
            <div style="text-align: center; padding: 20px 0;">
                <h1 style="margin: 0; background: linear-gradient(90deg, #FF6F61, #DE4D86); 
                -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5em;">
                MixTune
                </h1>
                <p style="margin: 0; color: #8282A6; margin-top: -5px;">AI Music Discovery</p>
            </div>
        """, unsafe_allow_html=True)

    # User profile section
    st.markdown("""
        <div class="user-profile">
            <div class="user-avatar">👤</div>
            <div>
                <div style="font-weight: bold;">{name}</div>
                <div style="font-size: 0.8em; color: #8282A6;">{status} Account</div>
            </div>
        </div>
    """.format(name=st.session_state.user_profile["name"], status=st.session_state.user_profile["status"]),
                unsafe_allow_html=True)

    # Statistics
    st.markdown("""
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <div style="text-align: center; flex: 1;">
                <div style="font-size: 1.5em; font-weight: bold;">{favorites}</div>
                <div style="font-size: 0.8em; color: #8282A6;">Favorites</div>
            </div>
            <div style="text-align: center; flex: 1;">
                <div style="font-size: 1.5em; font-weight: bold;">{playlist}</div>
                <div style="font-size: 0.8em; color: #8282A6;">Playlist</div>
            </div>
            <div style="text-align: center; flex: 1;">
                <div style="font-size: 1.5em; font-weight: bold;">{plays}</div>
                <div style="font-size: 0.8em; color: #8282A6;">Plays</div>
            </div>
        </div>
    """.format(
        favorites=len(st.session_state.favorites),
        playlist=len(st.session_state.playlist),
        plays=st.session_state.total_plays
    ), unsafe_allow_html=True)

    # Navigation with active state indication
    st.markdown("<p style='color: #8282A6; margin-bottom: 5px;'>NAVIGATION</p>", unsafe_allow_html=True)

    # List of navigation items
    nav_items = [
        "🏠 Home",
        "🎵 Recommendations",
        "🔍 Search",
        "📊 Visualizations",
        "❤️ Favorites",
        "🎶 Playlist"
    ]

    # Display navigation items with active state
    for item in nav_items:
        active_class = "active" if st.session_state.active_tab == item else ""
        if st.markdown(f"""
            <div class="sidebar-item {active_class}" id="{item}">
                {item}
            </div>
            """, unsafe_allow_html=True):
            st.session_state.active_tab = item
            st.rerun()

    # Settings section
    st.markdown("<p style='color: #8282A6; margin-bottom: 5px; margin-top: 20px;'>SETTINGS</p>", unsafe_allow_html=True)

    dark_mode = st.checkbox("Dark Mode", value=st.session_state.dark_mode)
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode

    quality_options = ["Standard", "High", "Ultra"]
    audio_quality = st.select_slider("Audio Quality", options=quality_options, value="High")

    # Upgrade prompt
    st.markdown("""
        <div style="background: linear-gradient(90deg, rgba(255, 111, 97, 0.15), rgba(222, 77, 134, 0.15)); 
                    padding: 15px; border-radius: 10px; margin-top: 20px;">
            <h4 style="margin: 0 0 10px 0;">Upgrade to Premium</h4>
            <p style="margin: 0 0 10px 0; font-size: 0.9em;">Get unlimited recommendations, higher audio quality, and exclusive features.</p>
            <div style="text-align: center;">
                <div style="background: linear-gradient(90deg, #FF6F61, #DE4D86); padding: 8px; border-radius: 8px; font-weight: bold; cursor: pointer;">
                    GO PREMIUM
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
        <div style="position: absolute; bottom: 20px; width: calc(100% - 30px); font-size: 0.8em; text-align: center; color: #8282A6;">
            MixTune v1.2.0 | © 2025 MixTune
        </div>
    """, unsafe_allow_html=True)

# Store the selected tab in session state for sidebar highlighting
selected_tab = st.session_state.active_tab

# Home Tab
if "Home" in selected_tab:
    st.markdown(
        "<div class='page-header'><h1>🎧 Welcome to MixTune</h1><p>Discover music tailored just for you!</p></div>",
        unsafe_allow_html=True)

    # Recently played section
    st.subheader("Recently Played")
    recent_cols = st.columns(4)
    for i in range(4):
        with recent_cols[i]:
            st.markdown(f"""
                <div style="background-color: #2D2D44; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <div style="height: 120px; background: linear-gradient(45deg, {['#FF6F61', '#DE4D86', '#9B72AA', '#5086C1'][i]}, rgba(45, 45, 68, 0.8)); 
                             display: flex; align-items: center; justify-content: center;">
                        <span style="font-size: 2.5em;">🎵</span>
                    </div>
                    <div style="padding: 10px;">
                        <div style="font-weight: bold;">{"Recent Song " + str(i + 1)}</div>
                        <div style="font-size: 0.8em; color: #8282A6;">Artist {i + 1}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    if data is not None:
        st.subheader("🎼 Top Songs by Popularity")
        if 'popularity' in data.columns and 'name' in data.columns and 'artists' in data.columns:
            top_songs = data.nlargest(5, 'popularity')[['name', 'artists', 'popularity']]

            for i, (_, song) in enumerate(top_songs.iterrows()):
                st.markdown(f"""
                    <div class="song-card">
                        <div class="song-info">
                            <div style="font-weight: bold;">{song['name']}</div>
                            <div style="font-size: 0.9em; color: #8282A6;">{song['artists']} • Popularity: {song['popularity']}</div>
                        </div>
                        <div class="song-actions">
                            <div class="action-button">▶️</div>
                            <div class="action-button">❤️</div>
                            <div class="action-button">➕</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Required columns ('name', 'artists', 'popularity') not found in the dataset.")
    else:
        st.error("Data not available to display top songs.")

    # For You section
    st.subheader("For You")
    genre_cols = st.columns(3)
    genres = ["Pop", "Rock", "Hip Hop"]
    colors = ["#FF6F61", "#5086C1", "#9B72AA"]

    for i, (genre, color) in enumerate(zip(genres, colors)):
        with genre_cols[i]:
            st.markdown(f"""
                <div style="background: linear-gradient(45deg, {color}, rgba(45, 45, 68, 0.8)); 
                         border-radius: 10px; padding: 20px; text-align: center; cursor: pointer;">
                    <h3>{genre}</h3>
                    <p style="margin: 0;">Discover more {genre.lower()} songs</p>
                </div>
            """, unsafe_allow_html=True)

# Recommendations Tab
elif "Recommendations" in selected_tab:
    st.markdown(
        "<div class='page-header'><h1>🎵 Personalized Song Recommendations</h1><p>Find your next favorite track</p></div>",
        unsafe_allow_html=True)

    if data is not None and model is not None:
        # Check if the required features exist in the data
        if 'name' not in data.columns:
            st.error("Column 'name' not found in the dataset.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                song_name = st.selectbox("Select a Song", data["name"].unique())
            with col2:
                top_n = st.slider("Number of Recommendations", 1, 10, 5)

            if st.button("Get Recommendations", key="get_recommendations"):
                with st.spinner("Generating recommendations..."):
                    try:
                        # Check if song exists in data
                        if song_name not in data["name"].values:
                            st.error(f"Song '{song_name}' not found in the dataset.")
                        else:
                            # Show a loading animation
                            st.markdown("<div class='loading-bar'></div>", unsafe_allow_html=True)

                            idx = data.index[data["name"] == song_name].tolist()[0]

                            # Check if model has feature_names_in_ attribute
                            if not hasattr(model, 'feature_names_in_'):
                                st.error(
                                    "Model doesn't have 'feature_names_in_' attribute. Please check model compatibility.")
                            else:
                                feature_columns = model.feature_names_in_

                                # Check if all required features exist in data
                                missing_features = [f for f in feature_columns if f not in data.columns]
                                if missing_features:
                                    st.error(f"Missing features in dataset: {missing_features}")
                                else:
                                    query_point = data.loc[idx, feature_columns].to_frame().T
                                    _, indices = model.kneighbors(query_point, n_neighbors=min(top_n + 1, len(data)))
                                    recommendations = [data.iloc[i]["name"] for i in indices[0][1:]]

                                    st.write(f"### Recommended Songs for '{song_name}'")

                                    # Display recommendations with action buttons
                                    for i, rec in enumerate(recommendations):
                                        rec_id = f"rec_{i}"
                                        # Get artist if available
                                        artist = data[data["name"] == rec]["artists"].values[
                                            0] if "artists" in data.columns else "Unknown Artist"

                                        st.markdown(f"""
                                            <div class="song-card">
                                                <div class="song-info">
                                                    <div style="font-weight: bold;">{rec}</div>
                                                    <div style="font-size: 0.9em; color: #8282A6;">{artist}</div>
                                                </div>
                                                <div class="song-actions">
                                                    <div class="action-button">▶️</div>
                                                </div>
                                            </div>
                                        """, unsafe_allow_html=True)

                                        # Use columns for buttons
                                        button_cols = st.columns([1, 1, 3])
                                        with button_cols[0]:
                                            if st.button("❤️ Favorite", key=f"fav_rec_{i}"):
                                                if add_to_favorites(rec):
                                                    st.success(f"Added {rec} to Favorites!")
                                                else:
                                                    st.info(f"{rec} is already in your Favorites!")

                                        with button_cols[1]:
                                            if st.button("➕ Playlist", key=f"playlist_rec_{i}"):
                                                if add_to_playlist(rec):
                                                    st.success(f"Added {rec} to Playlist!")
                                                else:
                                                    st.info(f"{rec} is already in your Playlist!")
                    except Exception as e:
                        st.error(f"Error generating recommendations: {e}")
                        st.info("Tip: Check if your model is compatible with the dataset.")
    else:
        st.error("Data or model not loaded. Please check file paths and try again.")

# Search Tab
elif "Search" in selected_tab:
    st.markdown("<div class='page-header'><h1>🔍 Song Search</h1><p>Find exactly what you're looking for</p></div>",
                unsafe_allow_html=True)

    # Add search filters
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Search for songs, artists or albums", placeholder="e.g., Imagine")
    with col2:
        search_filter = st.selectbox("Filter by", ["All", "Songs", "Artists", "Albums"])

    if data is not None:
        if 'name' not in data.columns or 'artists' not in data.columns:
            st.error("Required columns ('name', 'artists') not found in the dataset.")
        else:
            # Add advanced search options
            with st.expander("Advanced search options"):
                adv_cols = st.columns(3)
                with adv_cols[0]:
                    min_popularity = st.slider("Min. Popularity", 0, 100, 0)
                with adv_cols[1]:
                    if "year" in data.columns:
                        max_year = int(data["year"].max()) if not data["year"].empty else 2024
                        min_year = int(data["year"].min()) if not data["year"].empty else 1950
                        year_range = st.slider("Year range", min_year, max_year, (min_year, max_year))
                with adv_cols[2]:
                    sort_by = st.selectbox("Sort by", ["Relevance", "Popularity", "Year"])

            if search_query.strip():
                song_results = data[data["name"].str.contains(search_query, case=False, na=False)]
                if not song_results.empty:
                    st.write("### 🎵 Search Results")
                    for i, (_, row) in enumerate(song_results.iterrows()):
                        # Format additional info if available
                        additional_info = []
                        if "year" in row and not pd.isna(row["year"]):
                            additional_info.append(f"{int(row['year'])}")
                        if "popularity" in row and not pd.isna(row["popularity"]):
                            additional_info.append(f"Popularity: {row['popularity']:.1f}")

                        additional_text = " • ".join(additional_info)

                        st.markdown(f"""
                            <div class="song-card">
                                <div class="song-info">
                                    <div style="font-weight: bold;">{row['name']}</div>
                                    <div style="font-size: 0.9em; color: #8282A6;">{row['artists']}{' • ' + additional_text if additional_text else ''}</div>
                                </div>
                                <div class="song-actions">
                                    <div class="action-button">▶️</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                        cols = st.columns([1, 1, 3])
                        with cols[0]:
                            if st.button(f"❤️ Favorite", key=f"fav_{i}"):
                                if add_to_favorites(row['name']):
                                    st.success(f"{row['name']} added to Favorites!")
                                else:
                                    st.info(f"{row['name']} is already in your Favorites!")
                        with cols[1]:
                            if st.button(f"➕ Playlist", key=f"playlist_{i}"):
                                if add_to_playlist(row['name']):
                                    st.success(f"{row['name']} added to Playlist!")
                                else:
                                    st.info(f"{row['name']} is already in your Playlist!")
                else:
                    st.markdown("""
                        <div style="text-align: center; padding: 30px 0;">
                            <div style="font-size: 3em; margin-bottom: 10px;">🔍</div>
                            <h3>No results found</h3>
                            <p>Try different keywords or check your spelling</p>
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.error("Data not available for search.")

# Visualizations Tab
elif "Visualizations" in selected_tab:
    st.markdown(
        "<div class='page-header'><h1>📊 Music Insights</h1><p>Explore patterns and trends in music data</p></div>",
        unsafe_allow_html=True)

    # More appealing visualization selection
    vis_cols = st.columns(3)

    with vis_cols[0]:
        st.markdown("""
            <div style="background-color: rgba(255, 111, 97, 0.2); border-radius: 10px; padding: 15px; text-align: center; cursor: pointer;">
                <div style="font-size: 2em;">📊</div>
                <h4>Feature Distribution</h4>
                <p style="font-size: 0.8em;">Explore audio features distribution</p>
            </div>
        """, unsafe_allow_html=True)
        vis1_selected = st.button("Select", key="vis1_button")

    with vis_cols[1]:
        st.markdown("""
            <div style="background-color: rgba(80, 134, 193, 0.2); border-radius: 10px; padding: 15px; text-align: center; cursor: pointer;">
                <div style="font-size: 2em;">🔥</div>
                <h4>Correlation Heatmap</h4>
                <p style="font-size: 0.8em;">Discover relationships between features</p>
            </div>
        """, unsafe_allow_html=True)
        vis2_selected = st.button("Select", key="vis2_button")

    with vis_cols[2]:
        st.markdown("""
            <div style="background-color: rgba(222, 77, 134, 0.2); border-radius: 10px; padding: 15px; text-align: center; cursor: pointer;">
                <div style="font-size: 2em;">📈</div>
                <h4>Popularity Trends</h4>
                <p style="font-size: 0.8em;">See how popularity changes over years</p>
            </div>
        """, unsafe_allow_html=True)
        vis3_selected = st.button("Select", key="vis3_button")

    # Set selection based on buttons
    if vis1_selected:
        vis_choice = "Feature Distribution"
    elif vis2_selected:
        vis_choice = "Correlation Heatmap"
    elif vis3_selected:
        vis_choice = "Popularity Over Years"
    else:
        # Default visualization
        vis_choice = "Feature Distribution"

    # Display selected visualization
    st.subheader(f"Selected: {vis_choice}")

    if data is not None:
        if vis_choice == "Feature Distribution":
            # Get only numeric columns for feature selection
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            if not numeric_cols:
                st.error("No numeric columns found in the dataset for visualization.")
            else:
                default_feature = "danceability" if "danceability" in numeric_cols else numeric_cols[0]
                feature = st.selectbox("Feature", numeric_cols, index=numeric_cols.index(
                    default_feature) if default_feature in numeric_cols else 0)

                # Create histogram with error handling
                try:
                    fig = px.histogram(data, x=feature, nbins=50, title=f"Distribution of {feature.capitalize()}",
                                       color_discrete_sequence=['#FF6F61'])
                    # Customize appearance
                    fig.update_layout(
                        plot_bgcolor='#2D2D44',
                        paper_bgcolor='#2D2D44',
                        font_color='#FFFFFF'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Add descriptive statistics
                    st.markdown("### Feature Statistics")
                    stats_cols = st.columns(4)
                    with stats_cols[0]:
                        st.metric("Average", f"{data[feature].mean():.2f}")
                    with stats_cols[1]:
                        st.metric("Median", f"{data[feature].median():.2f}")
                    with stats_cols[2]:
                        st.metric("Min", f"{data[feature].min():.2f}")
                    with stats_cols[3]:
                        st.metric("Max", f"{data[feature].max():.2f}")
                except Exception as e:
                    st.error(f"Error creating histogram: {e}")

        elif vis_choice == "Correlation Heatmap":
                # Check for numeric columns
                numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
                if len(numeric_cols) < 2:
                    st.error("Need at least 2 numeric columns to create a correlation heatmap.")
                else:
                    # Let user select features for correlation
                    st.subheader("Select Features for Correlation Analysis")

                    # Default selections based on audio features if available
                    default_features = [col for col in
                                        ["danceability", "energy", "loudness", "tempo", "valence", "acousticness"]
                                        if col in numeric_cols]

                    # If we don't have enough default features, use the first 5 numeric columns
                    if len(default_features) < 2:
                        default_features = numeric_cols[:min(5, len(numeric_cols))]

                    selected_features = st.multiselect(
                        "Select features to correlate (min 2, max 10)",
                        options=numeric_cols,
                        default=default_features[:min(5, len(default_features))]
                    )

                    if len(selected_features) < 2:
                        st.warning("Please select at least 2 features for correlation analysis.")
                    elif len(selected_features) > 10:
                        st.warning("Too many features selected. Please select a maximum of 10 features.")
                    else:
                        try:
                            # Calculate correlation matrix
                            corr_matrix = data[selected_features].corr()

                            # Create heatmap
                            fig = px.imshow(
                                corr_matrix,
                                text_auto='.2f',
                                color_continuous_scale='RdBu_r',
                                title="Feature Correlation Heatmap",
                                zmin=-1, zmax=1
                            )

                            # Customize appearance
                            fig.update_layout(
                                plot_bgcolor='#2D2D44',
                                paper_bgcolor='#2D2D44',
                                font_color='#FFFFFF'
                            )

                            st.plotly_chart(fig, use_container_width=True)

                            # Add interpretation guide
                            with st.expander("Understanding Correlation Values"):
                                st.markdown("""
                                            ### How to Interpret Correlation Values

                                            - **+1.00**: Perfect positive correlation - as one variable increases, the other increases proportionally
                                            - **+0.75 to +0.99**: Strong positive correlation
                                            - **+0.50 to +0.74**: Moderate positive correlation
                                            - **+0.25 to +0.49**: Weak positive correlation
                                            - **0.00 to +0.24**: Very weak or no correlation
                                            - **0.00 to -0.24**: Very weak or no correlation
                                            - **-0.25 to -0.49**: Weak negative correlation
                                            - **-0.50 to -0.74**: Moderate negative correlation
                                            - **-0.75 to -0.99**: Strong negative correlation
                                            - **-1.00**: Perfect negative correlation - as one variable increases, the other decreases proportionally

                                            ### Strong Correlations in Your Data
                                            """)

                                # Find strong correlations (absolute value > 0.6) excluding self-correlations
                                strong_corr = []
                                for i in range(len(selected_features)):
                                    for j in range(i + 1, len(selected_features)):
                                        if abs(corr_matrix.iloc[i, j]) > 0.6:
                                            strong_corr.append((selected_features[i],
                                                                selected_features[j],
                                                                corr_matrix.iloc[i, j]))

                                if strong_corr:
                                    for feat1, feat2, corr_val in strong_corr:
                                        relation = "positive" if corr_val > 0 else "negative"
                                        st.markdown(
                                            f"- **{feat1}** and **{feat2}**: {corr_val:.2f} ({relation} correlation)")
                                else:
                                    st.markdown("No strong correlations (|r| > 0.6) found in the selected features.")

                        except Exception as e:
                            st.error(f"Error creating correlation heatmap: {e}")

        elif vis_choice == "Popularity Over Years":
            # Check if necessary columns exist
            if 'year' not in data.columns:
                st.error("Column 'year' not found in the dataset.")
            elif 'popularity' not in data.columns:
                st.error("Column 'popularity' not found in the dataset.")
            else:
                try:
                    # Create year-based trends
                    st.subheader("Popularity Trends Over Years")

                    # Prepare the data
                    yearly_data = data.groupby('year').agg({
                        'popularity': ['mean', 'median', 'std', 'count']
                    }).reset_index()

                    # Flatten the column names
                    yearly_data.columns = ['year', 'avg_popularity', 'median_popularity', 'std_popularity',
                                           'song_count']

                    # Let user choose metric
                    popularity_metric = st.radio(
                        "Choose popularity metric",
                        ["Average", "Median"],
                        horizontal=True
                    )

                    metric_col = 'avg_popularity' if popularity_metric == "Average" else 'median_popularity'

                    # Create line plot with song count as size
                    fig = px.scatter(
                        yearly_data,
                        x='year',
                        y=metric_col,
                        size='song_count',
                        hover_data=['song_count', 'std_popularity'],
                        labels={
                            'year': 'Year',
                            metric_col: f'{popularity_metric} Popularity',
                            'song_count': 'Number of Songs'
                        },
                        title=f"{popularity_metric} Song Popularity by Year",
                        color_discrete_sequence=['#DE4D86']
                    )

                    # Add trendline
                    fig.add_traces(
                        px.line(
                            yearly_data,
                            x='year',
                            y=metric_col,
                            color_discrete_sequence=['#FF6F61']
                        ).data[0]
                    )

                    # Customize appearance
                    fig.update_layout(
                        plot_bgcolor='#2D2D44',
                        paper_bgcolor='#2D2D44',
                        font_color='#FFFFFF',
                        xaxis=dict(tickmode='linear', dtick=5)
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Show data for top and bottom years
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Most Popular Years")
                        top_years = yearly_data.nlargest(5, metric_col)
                        for _, row in top_years.iterrows():
                            st.markdown(f"""
                                                <div style="background-color: rgba(222, 77, 134, 0.2); padding: 10px; border-radius: 5px; margin-bottom: 5px;">
                                                    <strong>{int(row['year'])}</strong>: {row[metric_col]:.2f} popularity ({row['song_count']} songs)
                                                </div>
                                            """, unsafe_allow_html=True)

                    with col2:
                        st.subheader("Least Popular Years")
                        bottom_years = yearly_data.nsmallest(5, metric_col)
                        for _, row in bottom_years.iterrows():
                            st.markdown(f"""
                                                <div style="background-color: rgba(80, 134, 193, 0.2); padding: 10px; border-radius: 5px; margin-bottom: 5px;">
                                                    <strong>{int(row['year'])}</strong>: {row[metric_col]:.2f} popularity ({row['song_count']} songs)
                                                </div>
                                            """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error creating popularity trends visualization: {e}")
        else:
            st.error("Data not available for visualization.")

        # Favorites Tab
    elif "Favorites" in selected_tab:
        st.markdown(
            "<div class='page-header'><h1>❤️ Your Favorites</h1><p>Songs you love, all in one place</p></div>",
            unsafe_allow_html=True)

        if not st.session_state.favorites:
            st.markdown("""
                            <div style="text-align: center; padding: 50px 0;">
                                <div style="font-size: 3em; margin-bottom: 10px;">💔</div>
                                <h3>No favorites yet</h3>
                                <p>Start adding songs you love to your favorites!</p>
                            </div>
                        """, unsafe_allow_html=True)
        else:
            # Display favorites with option to remove
            for i, fav in enumerate(st.session_state.favorites):
                fav_id = f"fav_{i}"

                # Find song details if available in the dataset
                song_details = None
                if data is not None and 'name' in data.columns:
                    song_match = data[data['name'] == fav]
                    if not song_match.empty:
                        # Get artist if available
                        artist = song_match['artists'].values[
                            0] if 'artists' in song_match.columns else "Unknown Artist"
                        # Get popularity if available
                        popularity = f" • Popularity: {song_match['popularity'].values[0]:.1f}" if 'popularity' in song_match.columns else ""
                        song_details = f"{artist}{popularity}"

                st.markdown(f"""
                                <div class="song-card">
                                    <div class="song-info">
                                        <div style="font-weight: bold;">{fav}</div>
                                        <div style="font-size: 0.9em; color: #8282A6;">
                                            {song_details if song_details else "Added to favorites"}
                                        </div>
                                    </div>
                                    <div class="song-actions">
                                        <div class="action-button">▶️</div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)

                cols = st.columns([1, 4])
                with cols[0]:
                    if st.button("🗑️ Remove", key=f"remove_fav_{i}"):
                        st.session_state.favorites.remove(fav)
                        st.success(f"Removed {fav} from favorites!")
                        st.rerun()

    # Playlist Tab
    elif "Playlist" in selected_tab:
        st.markdown(
            "<div class='page-header'><h1>🎶 Your Playlist</h1><p>Curate your perfect mix</p></div>",
            unsafe_allow_html=True)

        # Allow user to name their playlist
        playlist_name = st.text_input("Playlist Name", value="My Awesome Mix")

        if not st.session_state.playlist:
            st.markdown("""
                            <div style="text-align: center; padding: 50px 0;">
                                <div style="font-size: 3em; margin-bottom: 10px;">📝</div>
                                <h3>Your playlist is empty</h3>
                                <p>Add songs to create your perfect mix!</p>
                            </div>
                        """, unsafe_allow_html=True)
        else:
            # Add playlist controls
            cols = st.columns([1, 1, 3])
            with cols[0]:
                st.button("▶️ Play All")
            with cols[1]:
                st.button("🔀 Shuffle")

            # Display playlist items with drag handles
            for i, song in enumerate(st.session_state.playlist):
                song_id = f"playlist_{i}"

                # Find song details if available
                song_details = None
                if data is not None and 'name' in data.columns:
                    song_match = data[data['name'] == song]
                    if not song_match.empty:
                        # Get artist if available
                        artist = song_match['artists'].values[
                            0] if 'artists' in song_match.columns else "Unknown Artist"
                        # Get duration if available
                        duration = f" • {song_match['duration_ms'].values[0] / 60000:.2f} min" if 'duration_ms' in song_match.columns else ""
                        song_details = f"{artist}{duration}"

                st.markdown(f"""
                                <div class="song-card">
                                    <div style="margin-right: 10px; color: #8282A6;">
                                        {i + 1}
                                    </div>
                                    <div class="song-info">
                                        <div style="font-weight: bold;">{song}</div>
                                        <div style="font-size: 0.9em; color: #8282A6;">
                                            {song_details if song_details else "Added to playlist"}
                                        </div>
                                    </div>
                                    <div class="song-actions">
                                        <div class="action-button">▶️</div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)

                cols = st.columns([1, 1, 3])
                with cols[0]:
                    if st.button("🗑️ Remove", key=f"remove_playlist_{i}"):
                        st.session_state.playlist.remove(song)
                        st.success(f"Removed {song} from playlist!")
                        st.rerun()
                with cols[1]:
                    if i > 0 and st.button("⬆️", key=f"move_up_{i}"):
                        st.session_state.playlist[i], st.session_state.playlist[i - 1] = st.session_state.playlist[
                            i - 1], st.session_state.playlist[i]
                        st.rerun()

            # Calculate total duration if available
            if data is not None and 'name' in data.columns and 'duration_ms' in data.columns:
                total_duration_ms = 0
                found_songs = 0

                for song in st.session_state.playlist:
                    song_match = data[data['name'] == song]
                    if not song_match.empty and 'duration_ms' in song_match.columns:
                        total_duration_ms += song_match['duration_ms'].values[0]
                        found_songs += 1

                if found_songs > 0:
                    # Convert to minutes and seconds
                    total_minutes = int(total_duration_ms / 60000)
                    total_seconds = int((total_duration_ms % 60000) / 1000)

                    st.markdown(f"""
                                    <div style="margin-top: 20px; padding: 10px; background-color: #2D2D44; border-radius: 10px;">
                                        <span style="font-weight: bold;">Total Duration:</span> {total_minutes} min {total_seconds} sec ({found_songs} of {len(st.session_state.playlist)} songs)
                                    </div>
                                """, unsafe_allow_html=True)