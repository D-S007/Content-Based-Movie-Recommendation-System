import streamlit as st
import pickle
import pandas as pd
import requests
import os
from pathlib import Path

# Load API key from Streamlit secrets
try:
    API_KEY = st.secrets["TMDB_API_KEY"]
except KeyError:
    st.error("API key not found. Please configure secrets.toml")
    st.stop()

# Determine the base directory
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

def fetch_poster(movie_id):
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        )
        data = response.json()
        if 'poster_path' in data and data['poster_path']:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        else:
            return "https://via.placeholder.com/500x750?text=Poster+Not+Found"
    except Exception as e:
        st.error(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/500x750?text=Error+Loading+Poster"

def recommend(movie):
    try:
        movie_index = movies[movies["title"] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        
        recommended_movies = []
        recommended_movies_posters = []
        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_movies_posters.append(fetch_poster(movie_id))
        return recommended_movies, recommended_movies_posters
    except Exception as e:
        st.error(f"Error generating recommendations: {e}")
        return [], []

# Load data with error handling
try:
    movies_dict = pickle.load(open(MODELS_DIR / "movies_dict.pkl", 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open(MODELS_DIR / "similarity.pkl", 'rb'))
except FileNotFoundError:
    st.error("Model files not found. Please make sure the 'models' directory exists with the required files.")
    st.stop()
except Exception as e:
    st.error(f"Error loading model data: {e}")
    st.stop()

# Streamlit Layout improvements
st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# Custom CSS for the styling
st.markdown(
    """
    <style>
    body {
        background-color: #f1f1f1;
        font-family: 'Arial', sans-serif;
    }
    .title {
        text-align: center;
        font-size: 3em;
        color: #FF6347;
        margin-bottom: 40px;
        font-weight: bold;
    }
    .recommendation-card {
        background-color: #fff;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        padding: 10px;
        text-align: center;
        margin: 10px;
    }
    .movie-title {
        font-size: 1.1em;
        font-weight: bold;
        color: #333;
    }
    .movie-poster {
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        max-width: 200px;
        height: auto;
        margin-top: 10px;
    }
    .btn {
        background-color: #FF6347;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        border: none;
        font-size: 1em;
    }
    .btn:hover {
        background-color: #e5533d;
    }
    </style>
    """, unsafe_allow_html=True)

# Title of the app
st.markdown('<h1 class="title">Content-Based Movie Recommendation System</h1>', unsafe_allow_html=True)

# Movie selection dropdown
selected_movie_name = st.selectbox("Select a Movie from TMDB", movies['title'].values)

# Recommendation button
if st.button('Recommend', key="recommend_button", help="Get movie recommendations based on selected movie"):
    # Get recommendations
    names, posters = recommend(selected_movie_name)
    
    if names:  # Only display if we have recommendations
        # Display recommendations in a grid layout
        st.subheader("Recommended Movies")

        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.markdown(f'<div class="recommendation-card">', unsafe_allow_html=True)
                st.text(names[i])
                st.image(posters[i], use_container_width=True, caption=f'{names[i]}')
                st.markdown('</div>', unsafe_allow_html=True)