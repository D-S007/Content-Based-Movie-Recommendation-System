import streamlit as st
import pickle
import pandas as pd
import requests
import dotenv
import os

dotenv.load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

def fetch_poster(movie_id):
    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    )
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']


def recommend(movie):
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

#Load data
movies_dict = pickle.load(open('../models/movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('../models/similarity.pkl', 'rb'))

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

    # Display recommendations in a grid layout
    st.subheader("Recommended Movies")

    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            col.markdown(f'<div class="recommendation-card">', unsafe_allow_html=True)
            col.text(names[i])
            col.image(posters[i], use_container_width=True, caption=f'{names[i]}')
            col.markdown('</div>', unsafe_allow_html=True)