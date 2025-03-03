import streamlit as st
import pandas as pd
import joblib
import seaborn as sns
import matplotlib.pyplot as plt
import os
from sklearn.neighbors import NearestNeighbors

# Set Streamlit Page Configuration
st.set_page_config(page_title="Music Recommendation System", layout="wide")


# Function to Load Datasets
@st.cache_data
def load_data():
    try:
        data_path = r"D:/Music Recommendation System/MusicRecommendationSystem/data/"
        data = pd.read_csv(os.path.join(data_path, "data.csv"))
        data_by_artist = pd.read_csv(os.path.join(data_path, "data_by_artist.csv"))
        data_by_genres = pd.read_csv(os.path.join(data_path, "data_by_genres.csv"))
        data_by_year = pd.read_csv(os.path.join(data_path, "data_by_year.csv"))
        return data, data_by_artist, data_by_genres, data_by_year
    except Exception as e:
        st.error(f"Error loading datasets: {e}")
        return None, None, None, None


# Function to Load Trained Models
@st.cache_resource
def load_models():
    models = {}
    model_path = "D:/Music Recommendation System/MusicRecommendationSystem/"
    model_files = {
        "data": "data_model.pkl",
        "data_by_artist": "data_by_artist_model.pkl",
        "data_by_genres": "data_by_genres_model.pkl",
        "data_by_year": "data_by_year_model.pkl"
    }

    for key, filename in model_files.items():
        file_path = os.path.join(model_path, filename)
        if os.path.exists(file_path):
            models[key] = joblib.load(file_path)
        else:
            st.warning(f"⚠️ Model file not found: {file_path}")
            models[key] = None

    return models


# Load Data and Models
data, data_by_artist, data_by_genres, data_by_year = load_data()
models = load_models()

# Sidebar UI
st.sidebar.image("logo.png", use_column_width=True)
st.sidebar.title("🎵 Music Recommendation System")
selected_tab = st.sidebar.radio("Choose an Option", ["Home", "Recommendations", "Visualizations", "Top Trends"])

# Home Page
if selected_tab == "Home":
    st.title("🎧 AI-Powered Music Recommender")
    st.write("Get personalized song recommendations based on your preferences!")

    # Check if banner image exists before displaying
    if os.path.exists("music_banner.png"):
        st.image("music_banner.png", use_column_width=True)
    else:
        st.warning("⚠️ Banner image not found. Please check the file path!")

# Recommendations Tab
elif selected_tab == "Recommendations":
    st.subheader("🔍 Find Similar Songs, Artists, or Genres")
    entity_type = st.selectbox("Choose a category", ["Songs", "Artists", "Genres", "Year"])

    if entity_type == "Songs":
        column, dataset, model = "name", data, models.get("data")
    elif entity_type == "Artists":
        column, dataset, model = "artists", data_by_artist, models.get("data_by_artist")
    elif entity_type == "Genres":
        column, dataset, model = "genres", data_by_genres, models.get("data_by_genres")
    else:
        column, dataset, model = "year", data_by_year, models.get("data_by_year")

    if dataset is not None and model is not None:
        entity = st.selectbox(f"Select a {entity_type}", dataset[column].unique())
        top_n = st.slider("Number of Recommendations", 1, 10, 5)

        if st.button("Get Recommendations"):
            if entity in dataset[column].values:
                idx = dataset.index[dataset[column] == entity][0]

                # Get only the columns used during training
                feature_columns = model.feature_names_in_  # Extract trained feature names
                query_point = dataset.loc[idx, feature_columns].to_frame().T  # Ensure correct shape

                _, indices = model.kneighbors(query_point, n_neighbors=top_n + 1)
                recommendations = [dataset.iloc[i][column] for i in indices[0][1:]]

                st.write(f"### Recommendations for {entity}")
                for rec in recommendations:
                    st.write(f"🎵 {rec}")
            else:
                st.error(f"⚠️ The selected {entity_type} is not found in the dataset!")
    else:
        st.error("⚠️ Data or model not loaded properly. Please check the file paths.")

# Visualizations Tab
elif selected_tab == "Visualizations":
    st.subheader("📊 Data Visualizations")
    st.write("Explore trends and relationships in music data.")

    vis_choice = st.selectbox("Choose a visualization", ["Feature Correlation Heatmap", "Top 10 Artists", "Top Genres"])

    if data is not None:
        if vis_choice == "Feature Correlation Heatmap":
            numeric_data = data.select_dtypes(include=['number']).dropna()
            plt.figure(figsize=(10, 6))
            sns.heatmap(numeric_data.corr(), annot=True, cmap="coolwarm", fmt=".2f")
            st.pyplot(plt)

        elif vis_choice == "Top 10 Artists" and data_by_artist is not None:
            top_artists = data_by_artist.nlargest(10, "count")
            plt.figure(figsize=(12, 5))
            sns.barplot(y=top_artists["count"], x=top_artists["artists"], palette="magma")
            plt.xlabel("Artists")
            plt.ylabel("Number of Songs")
            plt.title("Top 10 Artists by Song Count")
            st.pyplot(plt)

        elif vis_choice == "Top Genres" and data_by_genres is not None:
            top_genres = data_by_genres.nlargest(10, "popularity")
            plt.figure(figsize=(12, 5))
            sns.barplot(y=top_genres["popularity"], x=top_genres["genres"], palette="viridis")
            plt.xlabel("Genres")
            plt.ylabel("Popularity Score")
            plt.title("Top 10 Genres by Popularity")
            st.pyplot(plt)
        else:
            st.error("⚠️ Data is missing for this visualization.")
    else:
        st.error("⚠️ Dataset not loaded. Please check file paths.")

# Top Trends Tab
elif selected_tab == "Top Trends":
    st.subheader("🔥 Top Trending Songs & Artists")

    if data is not None and data_by_artist is not None:
        top_songs = data.nlargest(10, "popularity")["name"]
        top_artists = data_by_artist.nlargest(10, "count")["artists"]

        st.write("### 🎶 Top 10 Trending Songs")
        for song in top_songs:
            st.write(f"🎵 {song}")

        st.write("### 🎤 Top 10 Trending Artists")
        for artist in top_artists:
            st.write(f"🎸 {artist}")
    else:
        st.error("⚠️ Data not loaded. Please check file paths.")

# Footer
st.sidebar.markdown("---")
st.sidebar.write("👨‍💻 Developed by Wasif Sohail")
