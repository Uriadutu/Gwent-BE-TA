import pandas as pd
import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from math import log10

# Fungsi membersihkan teks
def bersihkan_teks(teks: str) -> str:
    stop_factory = StopWordRemoverFactory()
    stopword_remover = stop_factory.create_stop_word_remover()
    teks = teks.lower()
    teks = re.sub(r"[^a-z0-9\s]", " ", teks)
    teks = stopword_remover.remove(teks)
    return teks.strip()

# Gabungkan fitur-fitur
def gabungkan_fitur(row):
    return f"{row['Judul']} {row['Penyanyi']} {row['Label']} {row['Genre']} {row['Lirik']}"

# Baca dan siapkan data
df = pd.read_csv("D:\\Projek Kawan\\TA\\GwentTA\\Backend\\data\\datadummy.csv", encoding='utf-8-sig')
df["combined"] = df.apply(gabungkan_fitur, axis=1)
df["cleaned"] = df["combined"].apply(bersihkan_teks)

print("\n=== 🔍 TEKS SETELAH DIBERSIHKAN ===")
print(df["cleaned"], "\n")

# Kata kunci
keyword_asli = "Penolong Setia"
keyword_cleaned = bersihkan_teks(keyword_asli)
keyword_terms = keyword_cleaned.split()
print("Kata kunci setelah dibersihkan:", keyword_terms, "\n")

# Hitung TF, DF, IDF, dan TF-IDF
N = len(df)
df_list = []
idf_dict = {}
tfidf_matrix = []

print("=== 📊 TF (Term Frequency) ===")
for i, row in enumerate(df["cleaned"]):
    tokens = row.split()
    total_terms = len(tokens)
    tf_doc = {}
    for term in keyword_terms:
        tf = tokens.count(term) / total_terms
        tf_doc[term] = tf
        df_list.append((term, i)) if term in tokens else None
    print(f"Doc {i + 1}:")
    for term, tf in tf_doc.items():
        print(f"  {term}: {tf:.4f}")
    tfidf_matrix.append(tf_doc)

# Hitung DF dan IDF
print("\n=== 📌 DF (Document Frequency) & IDF (Inverse Document Frequency) ===")
idf_vector = []
for term in keyword_terms:
    df_count = sum(term in row.split() for row in df["cleaned"])
    idf = log10(N / df_count) if df_count > 0 else 0
    idf_dict[term] = idf
    idf_vector.append(idf)
    print(f"{term} -> DF: {df_count}, IDF: {idf:.4f}")

# Hitung TF-IDF dan bentuk vektor dokumen
print("\n=== 🧠 TF-IDF ===")
doc_vectors = []
for i, tf_dict in enumerate(tfidf_matrix):
    vector = []
    print(f"Doc {i + 1}:")
    for term in keyword_terms:
        tfidf = tf_dict[term] * idf_dict[term]
        vector.append(tfidf)
        print(f"  {term}: TF-IDF = {tf_dict[term]:.4f} x {idf_dict[term]:.4f} = {tfidf:.4f}")
    doc_vectors.append(vector)

# Buat vektor kata kunci (anggap TF = 1 untuk setiap term, karena hanya dihitung dari input)
query_vector = [1 * idf_dict[term] for term in keyword_terms]

# Hitung cosine similarity
print("\n=== 📐 COSINE SIMILARITY KEYWORD vs DOKUMEN ===")
def cosine_sim(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    dot = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot / (norm_v1 * norm_v2) if norm_v1 and norm_v2 else 0.0

similarities = []
for i, vec in enumerate(doc_vectors):
    sim = cosine_sim(query_vector, vec)
    similarities.append((i, sim))
    print(f"Keyword vs Doc {i + 1}: {sim:.4f}")

# Tampilkan hasil rekomendasi
print("\n=== 🎵 RANKING REKOMENDASI ===")
sorted_sim = sorted(similarities, key=lambda x: x[1], reverse=True)
for idx, sim in sorted_sim:
    print(f"Rank {sorted_sim.index((idx, sim)) + 1}: Judul = {df.loc[idx, 'Judul']}, Skor = {sim:.4f}")
