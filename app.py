# streamlit_netflix_recommender_final.py
import streamlit as st
import pandas as pd
import pickle
from difflib import get_close_matches
from typing import List
import io
from PIL import Image, ImageDraw, ImageFont

# Page config
st.set_page_config(page_title="🎬 Netflex — Smart Recommender", layout="wide", page_icon="🎞️")

# --- Styles ---
st.markdown(
    """
    <style>
    .app-header {
        background: linear-gradient(90deg, #141e30, #243b55);
        color: white;
        padding: 16px 20px;
        border-radius: 12px;
    }
    .movie-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
        padding: 8px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(2,6,23,0.6);
        text-align: center;
    }
    .small-muted { color: #9aa6b2; font-size:12px }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Helpers ---
@st.cache_data
def load_data(movies_path: str = "movies.pkl", sim_path: str = "similarity.pkl"):
    try:
        movies = pickle.load(open(movies_path, "rb"))
        similarity = pickle.load(open(sim_path, "rb"))
    except FileNotFoundError as e:
        st.error(f"Required file not found: {e}")
        st.stop()
    return movies, similarity

def make_placeholder_image_bytes(text: str = "No Image", w: int = 300, h: int = 450) -> bytes:
    """
    Create a PNG placeholder using PIL and return bytes.
    Compatible with Pillow versions that removed textsize().
    """
    img = Image.new("RGB", (w, h), color=(43, 57, 75))
    draw = ImageDraw.Draw(img)

    # Try to use a simple font; fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font = ImageFont.load_default()

    text_wrapped = text if len(text) <= 20 else text[:17] + "..."

    # Cross-version text size calculation
    try:
        bbox = draw.textbbox((0, 0), text_wrapped, font=font)
        w_text = bbox[2] - bbox[0]
        h_text = bbox[3] - bbox[1]
    except Exception:
        # Older PIL fallback
        try:
            w_text, h_text = draw.textsize(text_wrapped, font=font)
        except Exception:
            w_text, h_text = (len(text_wrapped) * 6, 10)

    draw.text(((w - w_text) / 2, (h - h_text) / 2), text_wrapped, font=font, fill=(185, 199, 214))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()

def fuzzy_match(title: str, choices: List[str], n=5):
    title = title.strip().lower()
    lower_choices = [c.lower() for c in choices]
    if title in lower_choices:
        return [choices[lower_choices.index(title)]]
    matches = get_close_matches(title, lower_choices, n=n, cutoff=0.45)
    return [choices[lower_choices.index(m)] for m in matches]

# Classic simple recommend (your selectbox-style)
def simple_recommend(movie: str, movies: pd.DataFrame, similarity, k: int = 5):
    movie = movie.lower().strip()
    titles_lower = movies['title'].str.lower().values
    if movie not in titles_lower:
        return []
    movie_index = int(movies[movies['title'].str.lower() == movie].index[0])
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:k+1]
    return [movies.iloc[i[0]].title for i in movies_list]

# Recommendation logic (rich card-based)
def recommend(movie_title: str, movies: pd.DataFrame, similarity, k: int = 5):
    movie_title_clean = movie_title.strip().lower()
    lower_titles = movies['title'].str.lower().values
    if movie_title_clean not in lower_titles:
        # Try fuzzy matching
        close = fuzzy_match(movie_title, movies['title'].tolist(), n=1)
        if close:
            movie_title = close[0]
            movie_title_clean = movie_title.lower()
        else:
            return []
    movie_index = int(movies[movies['title'].str.lower() == movie_title_clean].index[0])
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:k+1]
    recommended = [movies.iloc[i[0]] for i in movies_list]
    return recommended

# --- Load ---
movies, similarity = load_data()

# Init session state
if 'last_search' not in st.session_state:
    st.session_state['last_search'] = ""
if 'search' not in st.session_state:
    st.session_state['search'] = movies['title'].iloc[0] if len(movies) > 0 else ""

# --- Layout ---
with st.container():
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    st.markdown("""
    <h2 style='margin:0;padding:0'>🎬 Netflex — Smart Recommender</h2>
    <div class='small-muted'>Both a teacher-friendly selectbox and a demo-ready card UI</div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([2, 3])

with col_left:
    st.subheader("Search / Controls")
    input_search = st.text_input("Search or type a movie title", value=st.session_state['search'])
    num = st.slider("Number of recommendations", 1, 10, 5)
    show_posters = st.checkbox("Show posters / thumbnails", value=True)
    st.write("---")
    st.markdown("**Dataset info**")
    st.write(f"Total movies: {len(movies)}")
    cols = movies.columns.tolist()
    st.write(f"Columns: {', '.join(cols[:6])}{'...' if len(cols)>6 else ''}")

    # Sync typed value into session_state
    if input_search != st.session_state.get('search'):
        st.session_state['search'] = input_search

    # --- Selectbox-style (teacher-friendly) ---
    st.write("---")
    st.subheader("Teacher-friendly: Selectbox")
    selected_movie = st.selectbox("Choose a movie from the list", movies['title'].values)
    if st.button("Get Selectbox Recommendations"):
        recs_simple = simple_recommend(selected_movie, movies, similarity, k=5)
        if not recs_simple:
            st.error("No recommendations found (selectbox).")
        else:
            st.markdown("**Recommended movies:**")
            for idx, t in enumerate(recs_simple, 1):
                st.write(f"{idx}. {t}")

with col_right:
    st.subheader("Quick picks")
    sample = movies['title'].sample(6, random_state=7).tolist() if len(movies) > 6 else movies['title'].tolist()
    buttons = st.columns(min(6, max(1, len(sample))))
    for i, b in enumerate(buttons):
        if b.button(sample[i], key=f"quick_{i}"):
            st.session_state['search'] = sample[i]

st.write("---")

search = st.session_state.get('search', movies['title'].iloc[0] if len(movies)>0 else "")

# Recommend when button pressed or search changed
if st.button("Recommend (Card UI)") or (search and st.session_state.get('last_search') != search):
    st.session_state['last_search'] = search
    with st.spinner("Finding good matches..."):
        recs = recommend(search, movies, similarity, k=num)

    if not recs:
        st.error("No recommendations found. Try a different title or check spelling.")
    else:
        st.subheader(f"Recommendations for: {search}")
        cols = st.columns(min(len(recs), 5))
        for i, movie_row in enumerate(recs):
            col = cols[i % len(cols)]
            with col:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)

                poster_shown = False
                if show_posters and 'poster_url' in movies.columns:
                    url = movie_row.get('poster_url')
                    if isinstance(url, str) and url.startswith('http'):
                        try:
                            st.image(url, use_column_width='always')
                            poster_shown = True
                        except Exception:
                            poster_shown = False

                if not poster_shown:
                    img_bytes = make_placeholder_image_bytes(movie_row.get('title', 'No Image'))
                    try:
                        st.image(img_bytes, use_column_width='always')
                    except Exception:
                        st.write("No image available")

                st.markdown(f"**{movie_row.get('title','Unknown Title')}**")
                if 'year' in movies.columns:
                    st.markdown(f"<div class='small-muted'>Year: {movie_row.get('year','—')}</div>", unsafe_allow_html=True)
                if 'genres' in movies.columns:
                    st.markdown(f"<div class='small-muted'>Genres: {movie_row.get('genres','—')}</div>", unsafe_allow_html=True)
                if 'imdb_id' in movies.columns and pd.notna(movie_row.get('imdb_id')):
                    imdb = movie_row.get('imdb_id')
                    imdb_link = f"https://www.imdb.com/title/{imdb}"
                    st.markdown(f"[View on IMDB]({imdb_link})")
                st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")
        st.success("Done — scroll up to view cards. You can toggle posters in the left panel.")

# Footer / tips
st.markdown("""
<div style='margin-top:18px;padding:12px;border-radius:8px;background:linear-gradient(180deg, #0f1724, #243b55);color:#cfe3ff'>
<strong>Tips for presentation:</strong>
<ul>
<li>Run: <code>python -m streamlit run streamlit_netflix_recommender_final.py</code></li>
<li>If posters don't appear, check whether your dataset has a <code>poster_url</code> column with valid HTTP URLs.</li>
<li>Want more polish? I can add hover effects, modal detail views, or fetch posters automatically from TMDB (requires an API key).</li>
</ul>
</div>
""", unsafe_allow_html=True)
