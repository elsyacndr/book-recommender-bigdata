import streamlit as st
import pandas as pd
import math

import os

# ===========================
# Folder data
# ===========================
BASE_DIR = os.path.dirname(__file__)  # folder app.py
DATA_DIR = os.path.join(BASE_DIR, "data")

books_path = os.path.join(DATA_DIR, "books_clean.csv")
recs_path = os.path.join(DATA_DIR, "user_recommendations.csv")

# ===========================
# Load data
# ===========================
if os.path.exists(books_path):
    books = pd.read_csv(books_path, low_memory=False)
else:
    st.error(f"File {books_path} tidak ditemukan!")
    books = pd.DataFrame()

if os.path.exists(recs_path):
    recs = pd.read_csv(recs_path)
else:
    st.error(f"File {recs_path} tidak ditemukan!")
    recs = pd.DataFrame()

# ===========================
# Page config
# ===========================
st.set_page_config(page_title="Book Recommender Elsya Candra", layout="wide")

# ===========================
# Load data
# ===========================
books = pd.read_csv("data/books_clean.csv", low_memory=False)
recs = pd.read_csv("data/user_recommendations.csv")

# ===========================
# Header & Identitas
# ===========================
st.title("📚 Book Recommender System Elsya")
st.markdown("""
Sistem rekomendasi buku menggunakan **Collaborative Filtering (ALS)**.  
Pilih User ID untuk melihat Top N rekomendasi buku lengkap dengan cover, penulis, rating, dan detail tambahan.  
<br>**Dibuat oleh:** Elsya Candra Nihaya Firdaus
""", unsafe_allow_html=True)

# ===========================
# Sidebar interaktif
# ===========================
with st.sidebar:
    st.header("🔧 Pengaturan")
    user_id = st.selectbox("Pilih User ID", sorted(recs["user_idx"].unique()))
    top_n = st.slider("Jumlah Rekomendasi", min_value=1, max_value=10, value=5)
    st.markdown("💡 **Tip:** Baris pertama Top 1-2 dibuat lebih menonjol, rating tinggi hijau, rendah merah muda.")

# ===========================
# Filter rekomendasi user
# ===========================
user_recs = recs[recs["user_idx"] == user_id]

# Mapping book_idx -> ISBN
book_mapping = books.reset_index()[["index", "ISBN"]].rename(columns={"index": "book_idx"})
user_recs_with_isbn = user_recs.merge(book_mapping, on="book_idx", how="left")

# Merge dengan buku untuk info lengkap
result = user_recs_with_isbn.merge(books, on="ISBN", how="left")\
    .sort_values("predicted_rating", ascending=False).head(top_n)

# ===========================
# Top N Rekomendasi User (Cards dengan UI berbeda tiap baris)
# ===========================
st.subheader(f"🔮 Top {top_n} Rekomendasi Buku Untuk User {user_id}")

max_cols = 5
num_books = len(result)
num_rows = math.ceil(num_books / max_cols)

for i in range(num_rows):
    start_idx = i * max_cols
    end_idx = start_idx + max_cols
    cols_in_row = min(max_cols, num_books - start_idx)
    cols = st.columns(cols_in_row)

    for j, (_, book) in enumerate(result.iloc[start_idx:end_idx].iterrows()):
        col = cols[j % cols_in_row]

        # Data default
        title = book['Book-Title'] if pd.notna(book['Book-Title']) else "Unknown Title"
        author = book['Book-Author'] if pd.notna(book['Book-Author']) else "Unknown Author"
        year = book['Year-Of-Publication'] if pd.notna(book['Year-Of-Publication']) else "—"
        publisher = book['Publisher'] if pd.notna(book['Publisher']) else "—"
        rating = book['predicted_rating'] if pd.notna(book['predicted_rating']) else 0.0
        cover_url = book["Image-URL-M"] if pd.notna(book["Image-URL-M"]) else "https://via.placeholder.com/120x180.png?text=No+Cover"

        # Baris pertama lebih besar & lebih shadow
        if i == 0:
            card_height = 380
            shadow = "4px 4px 20px rgba(0,0,0,0.3)"
        else:
            card_height = 380
            shadow = "2px 2px 10px rgba(0,0,0,0.15)"

        # Warna background berdasarkan rating
        if rating >= 4:
            bg_color = "#d4f7d4"  # hijau muda
        elif rating >= 3:
            bg_color = "#f9f9f9"  # abu muda
        else:
            bg_color = "#fff3f3"  # merah muda

        # Card HTML
        card_html = f"""
        <div style="
            background-color:{bg_color};
            padding:12px; 
            border-radius:12px; 
            text-align:center;
            box-shadow:{shadow};
            height:{card_height}px;
            margin-bottom:10px;
        ">
            <img src="{cover_url}" width="120"><br>
            <b>{title}</b><br>
            <i>{author}</i><br>
            ⭐ {rating:.2f}<br>
            📖 {year} | 🏢 {publisher}
        </div>
        """
        col.markdown(card_html, unsafe_allow_html=True)

# ===========================
# Buku Rating Tertinggi & Terendah User
# ===========================
st.subheader(f"📈 Buku Rating Tertinggi dan Terendah User {user_id}")
if num_books > 0:
    top_rated_user = result.sort_values("predicted_rating", ascending=False).iloc[0]
    lowest_rated_user = result.sort_values("predicted_rating", ascending=True).iloc[0]

    col1, col2 = st.columns(2)

    def display_user_card(col, book, title_card, bg_color, icon="⭐"):
        title = book['Book-Title'] if pd.notna(book['Book-Title']) else "Unknown Title"
        author = book['Book-Author'] if pd.notna(book['Book-Author']) else "Unknown Author"
        year = book['Year-Of-Publication'] if pd.notna(book['Year-Of-Publication']) else "—"
        publisher = book['Publisher'] if pd.notna(book['Publisher']) else "—"
        rating = book['predicted_rating'] if pd.notna(book['predicted_rating']) else 0.0
        cover_url = book["Image-URL-M"] if pd.notna(book["Image-URL-M"]) else "https://via.placeholder.com/140x210.png?text=No+Cover"

        card_html = f"""
        <div style="
            background-color:{bg_color};
            border-left: 6px solid #555;
            padding:14px;
            border-radius:14px;
            text-align:center;
            box-shadow:3px 3px 15px rgba(0,0,0,0.2);
            margin-bottom:12px;
        ">
            <h4>{icon} {title_card}</h4>
            <img src="{cover_url}" width="140"><br>
            <b>{title}</b><br>
            <i>{author}</i><br>
            ⭐ {rating:.2f}<br>
            📖 {year} | 🏢 {publisher}
        </div>
        """
        col.markdown(card_html, unsafe_allow_html=True)

    display_user_card(col1, top_rated_user, "Rating Tertinggi User", "#d4f7d4", "🏆")
    display_user_card(col2, lowest_rated_user, "Rating Terendah User", "#fff3f3", "⚠️")

# ===========================
# Buku Rating Tertinggi & Terendah Semua User (UI Premium)
# ===========================
st.subheader("📈 Buku Rating Tertinggi dan Terendah (Semua User)")

all_books_with_ratings = recs.merge(
    books.reset_index()[["index", "ISBN"]],
    left_on="book_idx",
    right_on="index",
    how="left"
).merge(books, on="ISBN", how="left")

top_rated_global = all_books_with_ratings.sort_values("predicted_rating", ascending=False).iloc[0]
lowest_rated_global = all_books_with_ratings.sort_values("predicted_rating", ascending=True).iloc[0]

col1, col2 = st.columns(2)

def display_global_card(col, book, title_card, border_color, bg_gradient, icon):
    title = book['Book-Title'] if pd.notna(book['Book-Title']) else "Unknown Title"
    author = book['Book-Author'] if pd.notna(book['Book-Author']) else "Unknown Author"
    year = book['Year-Of-Publication'] if pd.notna(book['Year-Of-Publication']) else "—"
    publisher = book['Publisher'] if pd.notna(book['Publisher']) else "—"
    rating = book['predicted_rating'] if pd.notna(book['predicted_rating']) else 0.0
    cover_url = book["Image-URL-M"] if pd.notna(book["Image-URL-M"]) else "https://via.placeholder.com/140x210.png?text=No+Cover"

    card_html = f"""
    <div style="
        background: {bg_gradient};
        border: 3px solid {border_color};
        padding:16px;
        border-radius:16px;
        text-align:center;
        box-shadow: 4px 4px 20px rgba(0,0,0,0.3);
        margin-bottom:12px;
    ">
        <span style="
            display:inline-block;
            background-color:{border_color};
            color:white;
            font-weight:bold;
            padding:4px 12px;
            border-radius:8px;
            margin-bottom:8px;
            font-size:14px;
        ">{icon} {title_card}</span>
        <br>
        <img src="{cover_url}" width="140"><br>
        <b style='font-size:16px'>{title}</b><br>
        <i style='color:#555'>{author}</i><br>
        ⭐ <b>{rating:.2f}</b><br>
        📖 {year} | 🏢 {publisher}
    </div>
    """
    col.markdown(card_html, unsafe_allow_html=True)

display_global_card(col1, top_rated_global, "Top Book Global", "#FFD700", "linear-gradient(135deg, #fffacd, #ffeb3b)", "🏆")
display_global_card(col2, lowest_rated_global, "Lowest Book Global", "#FF6347", "linear-gradient(135deg, #ffe5e0, #ff6347)", "⚠️")

# ===========================
# Statistik Sistem
# ===========================
st.subheader("📊 Statistik Sistem")
col1, col2, col3 = st.columns(3)
col1.metric("Total Buku", len(books))
col2.metric("Total User", recs["user_idx"].nunique())
col3.metric("Total Rekomendasi", len(recs))

# ===========================
# Tabel Data Lengkap
# ===========================
st.subheader("📖 Data Buku Lengkap")
st.dataframe(books)

st.subheader("👥 Data Rekomendasi Lengkap")
st.dataframe(recs)
