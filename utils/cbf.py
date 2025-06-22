import requests
import pandas as pd
import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory


def fetch_data():
    url = "http://localhost:8000/lagu"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching data: {response.status_code}")

def combine_features(row):
    genres = " ".join([g["nama"] for g in row.get("genres", [])])
    penyanyis = " ".join([p["nama"] for p in row.get("penyanyis", [])])
    labels = " ".join([l["nama"] for l in row.get("labels", [])])

    return f"{row.get('judul', '')} {genres} {penyanyis} {labels} {row.get('lirik', '')}"

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def find_best_match(keyword, df):
    matches = df[df['combined_features'].str.contains(keyword, case=False, na=False)]
    if matches.empty:
        return None
    return matches.iloc[0]
def recommend_by_keyword(keyword, df, top_n=5):
    factory = StopWordRemoverFactory()
    stop_words_indonesia = factory.get_stop_words()

    tfidf = TfidfVectorizer(stop_words=stop_words_indonesia)
    tfidf_matrix = tfidf.fit_transform(df['combined_features'])

    matched_row = find_best_match(keyword, df)
    if matched_row is None:
        raise ValueError("❌ Tidak ditemukan lagu yang cocok dengan kata kunci tersebut.")

    idx = matched_row.name
    sim_scores = list(enumerate(cosine_similarity(tfidf_matrix[idx], tfidf_matrix)[0]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_n + 1]

    recommended_indices = [i[0] for i in sim_scores]
    scores = [i[1] for i in sim_scores]

    recommendations = df.iloc[recommended_indices][['judul']].copy()
    recommendations['skor'] = scores

    return matched_row['judul'], recommendations


if __name__ == "__main__":
    try:
        data = fetch_data()
        df = pd.DataFrame(data)

        if df.empty:
            raise ValueError("Dataset kosong. Tidak ada lagu yang tersedia.")

        df['combined_features'] = df.apply(combine_features, axis=1)
        df['combined_features'] = df['combined_features'].apply(normalize_text)

        keyword = input("Masukkan kata kunci lagu (judul, penyanyi, genre, lirik, dll): ").strip()
        keyword = normalize_text(keyword)

        matched_title, recommendations = recommend_by_keyword(keyword, df)

        print(f"\n🔍 Hasil mirip dengan lagu: **{matched_title}**")
        print("\n🎵 Rekomendasi Lagu:")
        print(recommendations.to_string(index=False))

    except Exception as e:
        print("Terjadi kesalahan:", e)
