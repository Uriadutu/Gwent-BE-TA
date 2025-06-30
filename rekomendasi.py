from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import requests
import re
import math
import json
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

rekomendasi_router = APIRouter()


class ValidasiRequest(BaseModel):
    keywords: list[str]  # daftar keyword yang ingin divalidasi

def precision_at_k(predicted_ids, relevant_ids, k=5):
    predicted_k = predicted_ids[:k]
    true_positives = sum(1 for pid in predicted_k if pid in relevant_ids)
    return true_positives / k

def average_precision(predicted_ids, relevant_ids):
    hits = 0
    sum_precisions = 0.0
    for i, pid in enumerate(predicted_ids):
        if pid in relevant_ids:
            hits += 1
            sum_precisions += hits / (i + 1)
    return sum_precisions / len(relevant_ids) if relevant_ids else 0.0

class RekomendasiRequest(BaseModel):
    keyword: str

# Fungsi normalisasi teks
def normalize_text(text: str) -> str:
    factory = StopWordRemoverFactory()
    stop_remover = factory.create_stop_word_remover()
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    return stop_remover.remove(text)



@rekomendasi_router.post("/rekomendasi")
def rekomendasi_lagu(request: RekomendasiRequest):
    try:
        res = requests.get("http://localhost:8000/prapemroses")
        if res.status_code != 200:
            raise HTTPException(status_code=500, detail="Gagal mengambil data prapemroses")

        df = pd.DataFrame(res.json())
        if df.empty:
            raise HTTPException(status_code=404, detail="Data kosong")

        df['normalized'] = df['prosesing'].apply(normalize_text)
        keyword = normalize_text(request.keyword)

        keyword_terms = keyword.split()
        docs_tokenized = df['normalized'].apply(lambda x: x.split())

        # Hitung TF
        tf = []
        for tokens in docs_tokenized:
            total = len(tokens)
            freqs = {}
            for term in keyword_terms:
                freqs[term] = tokens.count(term) / total if total else 0
            tf.append(freqs)

        # Hitung DF
        df_counts = {}
        for term in keyword_terms:
            df_counts[term] = sum(term in tokens for tokens in docs_tokenized)

        # Hitung IDF
        N = len(df)
        idf = {}
        for term in keyword_terms:
            df_val = df_counts[term]
            idf[term] = math.log10(N / df_val) if df_val else 0

        # Hitung TF-IDF dokumen
        tfidf_docs = []
        for tf_row in tf:
            tfidf_row = {}
            for term in keyword_terms:
                tfidf_row[term] = tf_row[term] * idf[term]
            tfidf_docs.append(tfidf_row)

        # TF untuk keyword aktual
        keyword_tokens = keyword.split()
        total_keyword_terms = len(keyword_tokens)
        tf_keyword = {}
        for term in keyword_terms:
            tf_keyword[term] = keyword_tokens.count(term) / total_keyword_terms if total_keyword_terms else 0

        keyword_vector = {term: tf_keyword[term] * idf[term] for term in keyword_terms}

        def cosine_manual(vec1, vec2):
            dot = sum(vec1[t] * vec2[t] for t in keyword_terms)
            norm1 = math.sqrt(sum(vec1[t] ** 2 for t in keyword_terms))
            norm2 = math.sqrt(sum(vec2[t] ** 2 for t in keyword_terms))
            return dot / (norm1 * norm2) if norm1 and norm2 else 0.0

        # Hitung cosine scores dan masukkan ke DataFrame
        cosine_scores = [cosine_manual(keyword_vector, row) for row in tfidf_docs]
        df["cosine_score"] = cosine_scores

        # Ambil dokumen dengan cosine = 1.0
        top_df = df[df["cosine_score"].round(4) == 1.000]

        # Jika kurang dari 5, tambahkan dari dokumen tertinggi lainnya
        if len(top_df) < 5:
            tambahan_df = df[~df.index.isin(top_df.index)].sort_values(by="cosine_score", ascending=False)
            top_df = pd.concat([top_df, tambahan_df.head(5 - len(top_df))])

        # Urutkan berdasarkan skor tertinggi dan ambil 5
        top_df = top_df.sort_values(by="cosine_score", ascending=False).head(5)

        hasil = []
        for _, row in top_df.iterrows():
            lagu_id = int(row["id_lagu"])
            lagu_response = requests.get(f"http://localhost:8000/lagu/{lagu_id}")
            if lagu_response.status_code != 200:
                continue
            lagu_data = lagu_response.json()
            hasil.append({
                "id": lagu_data.get("id", "-"),
                "judul": lagu_data.get("judul", "-"),
                "penyanyi": [p.get("nama", "-") for p in lagu_data.get("penyanyi_list", [])],
                "tahun": lagu_data.get("tahun_rilis", "-"),
                "skor_kemiripan": round(float(row["cosine_score"]), 4),
                "link": lagu_data.get("link", "-"),
                "genre": lagu_data.get("genre_list", []),
                "label": list({p.get("label") for p in lagu_data.get("penyanyi_list", []) if p.get("label")})
            })

        # Tetapkan yang paling cocok
        best_idx = int(df["cosine_score"].idxmax())
        best_score = df.loc[best_idx, "cosine_score"]
        judul_tercocok = df.loc[best_idx, "prosesing"]

        return {
            "keyword_dipakai": request.keyword,
            "judul_tercocok": judul_tercocok,
            "skor_tertinggi": round(float(best_score), 4),
            "rekomendasi": hasil
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
      
@rekomendasi_router.post("/pemrosesan")
def pemrosesan_lagu(request: RekomendasiRequest):
    try:
        res = requests.get("http://localhost:8000/prapemroses")
        if res.status_code != 200:
            raise HTTPException(status_code=500, detail="Gagal mengambil data")

        df = pd.DataFrame(res.json())
        if df.empty:
            raise HTTPException(status_code=404, detail="Data kosong")

        df['normalized'] = df['prosesing'].apply(normalize_text)
        keyword = normalize_text(request.keyword)

        keyword_terms = keyword.split()
        docs_tokenized = df['normalized'].apply(lambda x: x.split())

        # Hitung TF
        tf = []
        for tokens in docs_tokenized:
            total = len(tokens)
            freqs = {}
            for term in keyword_terms:
                freqs[term] = tokens.count(term) / total if total else 0
            tf.append(freqs)

        # Hitung DF
        df_counts = {}
        for term in keyword_terms:
            df_counts[term] = sum(term in tokens for tokens in docs_tokenized)

        # Hitung IDF
        N = len(df)
        idf = {}
        for term in keyword_terms:
            df_val = df_counts[term]
            idf[term] = math.log10(N / df_val) if df_val else 0

        # Hitung TF-IDF dokumen
        tfidf_docs = []
        for tf_row in tf:
            tfidf_row = {}
            for term in keyword_terms:
                tfidf_row[term] = tf_row[term] * idf[term]
            tfidf_docs.append(tfidf_row)

        # Hitung TF untuk keyword
        keyword_tokens = keyword.split()
        total_keyword_terms = len(keyword_tokens)
        tf_keyword = {}
        for term in keyword_terms:
            tf_keyword[term] = keyword_tokens.count(term) / total_keyword_terms if total_keyword_terms else 0

        # Hitung TF-IDF keyword dengan TF aktual
        keyword_vector = {term: tf_keyword[term] * idf[term] for term in keyword_terms}

        def cosine_manual(vec1, vec2):
            dot = sum(vec1[t] * vec2[t] for t in keyword_terms)
            norm1 = math.sqrt(sum(vec1[t] ** 2 for t in keyword_terms))
            norm2 = math.sqrt(sum(vec2[t] ** 2 for t in keyword_terms))
            return dot / (norm1 * norm2) if norm1 and norm2 else 0.0

        # Hitung cosine similarity untuk semua dokumen
        cosine_scores = [cosine_manual(keyword_vector, row) for row in tfidf_docs]
        df["cosine_score"] = cosine_scores

        # Ambil dokumen yang memiliki skor cosine 1.0000
        top_df = df[df["cosine_score"].round(4) == 1.000]

        # Jika kurang dari 5, tambahkan dari dokumen tertinggi berikutnya
        if len(top_df) < 5:
            tambahan_df = df[~df.index.isin(top_df.index)].sort_values(by="cosine_score", ascending=False)
            top_df = pd.concat([top_df, tambahan_df.head(5 - len(top_df))])

        # Ambil top 5 rekomendasi
        top_df = top_df.sort_values(by="cosine_score", ascending=False).head(5)

        hasil = []
        for _, row in top_df.iterrows():
            lagu_id = int(row['id_lagu'])
            lagu_response = requests.get(f"http://localhost:8000/lagu/{lagu_id}")
            if lagu_response.status_code != 200:
                continue
            lagu_data = lagu_response.json()
            hasil.append({
                "id": lagu_data.get("id", "-"),  # ← ini menampilkan id lagu
                "penyanyi": [p.get("nama", "-") for p in lagu_data.get("penyanyi_list", [])],
                "judul": lagu_data.get("judul", "-"),
                "tahun": lagu_data.get("tahun_rilis", "-"),
                "skor_kemiripan": round(float(row['cosine_score']), 4),
                "link": lagu_data.get("link", "-"),
                "genre": lagu_data.get("genre_list", []),
                "label": list({p.get("label") for p in lagu_data.get("penyanyi_list", []) if p.get("label")}),
                "vektor_index": int(row.name)
            })


        # Tentukan dokumen terbaik
        best_idx = int(df["cosine_score"].idxmax())
        best_score = df.loc[best_idx, "cosine_score"]

        return {
            "keyword_asli": request.keyword,
            "keyword_setelah_normalisasi": keyword,
            "jumlah_data_dibandingkan": int(N),
            "judul_tercocok": str(df.iloc[best_idx]['prosesing']),
            "nilai_cosine_tertinggi": round(float(best_score), 4),
            "step_by_step": {
                "tf_dokumen": [
                    {k: round(freqs[k], 4) for k in keyword_terms}
                    for freqs in tf
                ],
                "df": {k: int(v) for k, v in df_counts.items()},
                "idf": {k: round(v, 4) for k, v in idf.items()},
                "tf_keyword": {k: round(v, 4) for k, v in tf_keyword.items()},
                "tfidf_keyword": {k: round(v, 4) for k, v in keyword_vector.items()},
                "tfidf_dokumen": [
                    {k: round(row[k], 4) for k in keyword_terms} for row in tfidf_docs
                ],
                "cosine_scores_semua_dokumen": [round(float(s), 4) for s in cosine_scores],
                "corpus": df['normalized'].tolist()
            },
            "top_5_rekomendasi": hasil
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def normalisasi(text: str) -> str:
    return text.strip().lower()

GT_FILE = "data/likes.json"
    
@rekomendasi_router.get("/validasi")
def hitung_evaluasi_sederhana():
    try:
        if not os.path.exists(GT_FILE):
            raise HTTPException(status_code=500, detail="File ground truth tidak ditemukan")

        with open(GT_FILE, "r", encoding="utf-8") as f:
            ground_truth = json.load(f)

        total_keyword = len(ground_truth)
        if total_keyword == 0:
            raise HTTPException(status_code=400, detail="Data ground truth kosong")

        detail = []
        hit_list = []
        mrr_list = []
        ndcg_list = []

        K = 5  # Top-K

        for keyword, value in ground_truth.items():
            recommended = value.get("recommended", [])[:K]
            relevan_map = value.get("relevan", {})

            # Normalisasi
            recommended = [r.lower().strip() for r in recommended]
            relevan = {k.lower().strip(): v for k, v in relevan_map.items()}

            dcg = 0.0
            mrr = 0.0
            hit = 0

            for i, pred in enumerate(recommended):
                if pred in relevan:
                    hit = 1
                    if mrr == 0.0:
                        mrr = 1.0 / (i + 1)
                    dcg += 1.0 / math.log2(i + 2)  # posisi i dimulai dari 0

            # Ideal DCG dihitung dari relevansi aktual
            ideal_relevansi_sorted = sorted(relevan.values())
            ideal_dcg = sum([1.0 / math.log2(i + 2) for i in range(min(len(ideal_relevansi_sorted), K))])

            ndcg = dcg / ideal_dcg if ideal_dcg > 0 else 0.0

            hit_list.append(hit)
            mrr_list.append(mrr)
            ndcg_list.append(ndcg)

            detail.append({
                "keyword": keyword,
                "recommended": recommended,
                "relevan": list(relevan.keys()),
                f"Hit@{K}": hit,
                f"MRR@{K}": round(mrr, 4),
                f"nDCG@{K}": round(ndcg, 4)
            })

        return {
            "jumlah_keyword_divalidasi": total_keyword,
            f"HitRate@{K}": round(sum(hit_list) / total_keyword, 4),
            f"MRR@{K}": round(sum(mrr_list) / total_keyword, 4),
            f"nDCG@{K}": round(sum(ndcg_list) / total_keyword, 4),
            "detail": detail
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))