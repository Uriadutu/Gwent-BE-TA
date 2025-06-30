from sqlalchemy.orm import Session
from models import Lagu, Penyanyi, Genre, Label, Prapemrosesan
from utils.preprocessing import bersihkan_teks

# Ambil semua lagu
def get_all_lagu(db: Session):
    lagu_list = db.query(Lagu).all()
    result = []

    for l in lagu_list:
        penyanyis = [{"id": p.id, "nama": p.nama, "label": p.label.nama_label if p.label else "-"} for p in l.penyanyi_list]
        result.append({
            "id": l.id,
            "judul": l.judul,
            "tahun_rilis": l.tahun_rilis,
            "lirik": l.lirik,
            "link": l.link,
            "penyanyi_list": penyanyis,
            "genre_list": [g.nama for g in l.genre_list]
        })

    return result


# Ambil lagu berdasarkan ID
def get_lagu_by_id(db: Session, lagu_id: int):
    l = db.query(Lagu).filter(Lagu.id == lagu_id).first()
    if not l:
        return None

    penyanyis = [{"id": p.id, "nama": p.nama, "label": p.label.nama_label if p.label else "-"} for p in l.penyanyi_list]

    return {
        "id": l.id,
        "judul": l.judul,
        "tahun_rilis": l.tahun_rilis,
        "lirik": l.lirik,
        "link": l.link,
        "penyanyi_list": penyanyis,
        "genre_list": [g.nama for g in l.genre_list]
    }

def create_lagu(db: Session, data: dict):
    judul = data.get("judul")
    tahun_rilis = data.get("tahun_rilis")
    lirik = data.get("lirik")
    link = data.get("link")
    penyanyi_ids = data.get("penyanyi_ids", [])
    genre_ids = data.get("genre_ids", [])

    if not judul or not penyanyi_ids:
        raise ValueError("Judul dan daftar penyanyi wajib diisi.")

    penyanyis = db.query(Penyanyi).filter(Penyanyi.id.in_(penyanyi_ids)).all()
    if not penyanyis:
        raise ValueError("Tidak ditemukan penyanyi dengan ID yang diberikan.")

    genres = db.query(Genre).filter(Genre.id.in_(genre_ids)).all()

    # Buat objek Lagu
    lagu = Lagu(
        judul=judul,
        tahun_rilis=tahun_rilis,
        lirik=lirik,
        link=link,
        penyanyi_list=penyanyis,
        genre_list=genres
    )

    db.add(lagu)
    db.commit()
    db.refresh(lagu)

    # 🔁 Proses data untuk Prapemrosesan
    genre_joined = ", ".join([g.nama for g in genres])
    penyanyi_nama = ", ".join([p.nama for p in penyanyis])
    label_nama = ", ".join([p.label.nama_label if p.label else "-" for p in penyanyis])

    # Gabungkan semua teks
    combined_text = f"{judul} {penyanyi_nama} {label_nama} {genre_joined} {lirik or ''} {tahun_rilis or ''}"
    hasil_prosesing = bersihkan_teks(combined_text)

    # Simpan ke tabel prapemrosesan
    praproses = Prapemrosesan(
        id_lagu=lagu.id,
        prosesing=hasil_prosesing
    )
    db.add(praproses)
    db.commit()

    return lagu

# Update lagu
def update_lagu(db: Session, lagu_id: int, data: dict):
    lagu = db.query(Lagu).filter(Lagu.id == lagu_id).first()
    if not lagu:
        return None

    # Update atribut dasar
    lagu.judul = data.get("judul", lagu.judul)
    lagu.tahun_rilis = data.get("tahun_rilis", lagu.tahun_rilis)
    lagu.lirik = data.get("lirik", lagu.lirik)
    lagu.link = data.get("link", lagu.link)

    # Update relasi penyanyi jika dikirim
    if "penyanyi_ids" in data:
        penyanyi_ids = data["penyanyi_ids"]
        lagu.penyanyi_list = db.query(Penyanyi).filter(Penyanyi.id.in_(penyanyi_ids)).all()

    # Update relasi genre jika dikirim
    if "genre_ids" in data:
        genre_ids = data["genre_ids"]
        lagu.genre_list = db.query(Genre).filter(Genre.id.in_(genre_ids)).all()

    db.commit()
    db.refresh(lagu)

    # Rebuild teks untuk prapemrosesan
    genre_joined = ", ".join([g.nama for g in lagu.genre_list])
    penyanyi_nama = ", ".join([p.nama for p in lagu.penyanyi_list])
    label_nama = ", ".join([p.label.nama_label if p.label else "-" for p in lagu.penyanyi_list])

    combined_text = f"{lagu.judul} {penyanyi_nama} {label_nama} {genre_joined} {lagu.lirik or ''} {lagu.tahun_rilis or ''}"
    hasil_prosesing = bersihkan_teks(combined_text)

    # Update atau buat ulang entri prapemrosesan
    praproses = db.query(Prapemrosesan).filter(Prapemrosesan.id_lagu == lagu.id).first()
    if praproses:
        praproses.prosesing = hasil_prosesing
    else:
        praproses = Prapemrosesan(id_lagu=lagu.id, prosesing=hasil_prosesing)
        db.add(praproses)

    db.commit()
    return lagu

# Hapus lagu
def delete_lagu(db: Session, lagu_id: int):
    lagu = db.query(Lagu).filter(Lagu.id == lagu_id).first()
    if not lagu:
        return None

    db.delete(lagu)
    db.commit()
    return lagu

# Genre lagu
def get_genre_by_lagu(db: Session, lagu_id: int):
    lagu = db.query(Lagu).filter(Lagu.id == lagu_id).first()
    if lagu:
        return lagu.genre_list
    return []


# Penyanyi lagu
def get_penyanyi_by_lagu(db: Session, lagu_id: int):
    lagu = db.query(Lagu).filter(Lagu.id == lagu_id).first()
    if lagu:
        return lagu.penyanyi_list
    return []


# Label lagu
def get_label_by_lagu(db: Session, lagu_id: int):
    lagu = db.query(Lagu).filter(Lagu.id == lagu_id).first()
    if lagu:
        return [p.label for p in lagu.penyanyi_list if p.label]
    return []

def get_lagu_by_judul(db: Session, judul: str):
    return db.query(Lagu).filter(Lagu.judul == judul).first()
