from fastapi import FastAPI, HTTPException, Depends, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import re

from database import SessionLocal, engine
from models import Base
from controllers.LaguController import (
    get_all_lagu,
    get_lagu_by_id,
    get_lagu_by_judul,
    create_lagu,
    update_lagu,
    delete_lagu,
    get_genre_by_lagu,
    get_penyanyi_by_lagu,
    get_label_by_lagu
)

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RekomendasiRequest(BaseModel):
    keyword: str


def normalize_text(text: str) -> str:
    if not text:
        return ""
    factory = StopWordRemoverFactory()
    stop_remover = factory.create_stop_word_remover()
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = stop_remover.remove(text)
    return text


def combine_features(row):
    return f"{row.get('judul', '')} {row.get('penyanyi', '')} {row.get('genre', '')} {row.get('lirik', '')}"


def find_best_match(keyword: str, df: pd.DataFrame):
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df['combined_features'])
    keyword_vec = tfidf.transform([keyword])
    cosine_sim = cosine_similarity(keyword_vec, tfidf_matrix)
    best_match_idx = cosine_sim[0].argmax()
    best_score = cosine_sim[0][best_match_idx]
    return df.iloc[best_match_idx] if best_score > 0 else None


@app.get("/lagu")
def read_lagu_list(db: Session = Depends(get_db)):
    return get_all_lagu(db)


@app.get("/lagu/{lagu_id}")
def read_lagu(lagu_id: int, db: Session = Depends(get_db)):
    lagu = get_lagu_by_id(db, lagu_id)
    if not lagu:
        raise HTTPException(status_code=404, detail="Lagu tidak ditemukan")
    return lagu


@app.get("/lagu/judul/{judul}")
def read_lagu_by_judul(judul: str, db: Session = Depends(get_db)):
    lagu = get_lagu_by_judul(db, judul)
    if not lagu:
        raise HTTPException(status_code=404, detail="Lagu tidak ditemukan")
    return lagu


@app.post("/lagu")
def create_new_lagu(data: dict = Body(...), db: Session = Depends(get_db)):
    return create_lagu(db, data)


@app.put("/lagu/{lagu_id}")
def update_existing_lagu(lagu_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    lagu = update_lagu(db, lagu_id, data)
    if not lagu:
        raise HTTPException(status_code=404, detail="Lagu tidak ditemukan")
    return lagu


@app.delete("/lagu/{lagu_id}")
def delete_existing_lagu(lagu_id: int, db: Session = Depends(get_db)):
    lagu = delete_lagu(db, lagu_id)
    if not lagu:
        raise HTTPException(status_code=404, detail="Lagu tidak ditemukan")
    return {"message": f"Lagu dengan ID {lagu_id} berhasil dihapus"}


@app.post("/rekomendasi")
def rekomendasi_lagu(request: RekomendasiRequest):
    
    try:
        print("Keyword diterima:", request.keyword)

        url = "http://localhost:8000/lagu"
        response = requests.get(url)
        print("Status fetch data:", response.status_code)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Gagal mengambil data lagu")

        data = response.json()
        df = pd.DataFrame(data)
        print("Kolom yang tersedia:", df.columns.tolist())

        if df.empty:
            raise HTTPException(status_code=404, detail="Dataset lagu kosong")

        # Gabungkan fitur
        df['combined_features'] = df.apply(combine_features, axis=1)
        df['combined_features'] = df['combined_features'].apply(normalize_text)

        keyword = normalize_text(request.keyword)

        matched_row = find_best_match(keyword, df)
        if matched_row is None:
            raise HTTPException(status_code=404, detail="Lagu tidak ditemukan berdasarkan keyword")

        idx = matched_row.name

        # Hitung kemiripan antar lagu
        factory = StopWordRemoverFactory()
        stop_words = factory.get_stop_words()
        tfidf = TfidfVectorizer(stop_words=stop_words)
        tfidf_matrix = tfidf.fit_transform(df['combined_features'])
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:6]

        hasil = []
        for i, score in sim_scores:
            lagu = df.iloc[i]

            # Ambil nama genre, penyanyi, label
            genres = [g["nama"] for g in lagu.get("genres", [])]
            penyanyis = [p["nama"] for p in lagu.get("penyanyis", [])]
            labels = [l["nama"] for l in lagu.get("labels", [])]

            hasil.append({
                "judul": lagu.get("judul", "-"),
                "penyanyi": penyanyis,
                "tahun": lagu.get("tahun_rilis", "-"),
                "skor_kemiripan": round(score, 3),
                "link": lagu.get("link", "-"),
                "genre": genres,
                "label": labels
            })

        return {
            "keyword_dipakai": request.keyword,
            "cocok_dengan_lagu": matched_row.get("judul", "-"),
            "rekomendasi": hasil
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/lagu/{lagu_id}/genres")
def read_genres_by_lagu(lagu_id: int, db: Session = Depends(get_db)):
    return get_genre_by_lagu(db, lagu_id)

@app.get("/lagu/{lagu_id}/penyanyis")
def read_penyanyis_by_lagu(lagu_id: int, db: Session = Depends(get_db)):
    return get_penyanyi_by_lagu(db, lagu_id)

@app.get("/lagu/{lagu_id}/labels")
def read_labels_by_lagu(lagu_id: int, db: Session = Depends(get_db)):
    return get_label_by_lagu(db, lagu_id)
