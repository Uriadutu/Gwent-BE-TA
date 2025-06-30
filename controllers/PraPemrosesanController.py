from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Lagu, Prapemrosesan
from utils.preprocessing import bersihkan_teks

# Simpan data lagu yang sudah diproses ke tabel prapemrosesan
def proses_dan_simpan_prapemrosesan(id_lagu: int, db: Session):
    lagu = db.query(Lagu).filter(Lagu.id == id_lagu).first()
    if not lagu:
        raise HTTPException(status_code=404, detail="Lagu tidak ditemukan")

    existing = db.query(Prapemrosesan).filter(Prapemrosesan.id_lagu == id_lagu).first()
    if existing:
        raise HTTPException(status_code=400, detail="Data sudah ada di prapemrosesan")

    # Ambil data dari relasi
    genre_joined = " ".join([g.nama for g in lagu.genre_list] if lagu.genre_list else [])
    penyanyi_nama = lagu.penyanyi.nama if lagu.penyanyi else ""
    label_nama = lagu.penyanyi.label.nama_label if lagu.penyanyi and lagu.penyanyi.label else ""
    
    # Gabungkan semua fitur menjadi satu string
    combined_text = f"{lagu.judul} {penyanyi_nama} {label_nama} {genre_joined} {lagu.lirik or ''}"

    # Lakukan pra-pemrosesan
    hasil_praproses = " ".join(bersihkan_teks(combined_text))

    # Simpan ke tabel
    praproses = Prapemrosesan(
        id_lagu=lagu.id,
        prosesing=hasil_praproses
    )

    db.add(praproses)
    db.commit()
    db.refresh(praproses)

    return {
        "message": "✅ Berhasil disimpan ke tabel prapemrosesan",
        "data": {
            "id_lagu": praproses.id_lagu,
            "prosesing": praproses.prosesing
        }
    }

# 🔍 Get semua data prapemrosesan
def get_all_prapemrosesan(db: Session):
    return db.query(Prapemrosesan).all()

# 🔍 Get prapemrosesan berdasarkan ID lagu
def get_prapemrosesan_by_id(id_lagu: int, db: Session):
    data = db.query(Prapemrosesan).filter(Prapemrosesan.id_lagu == id_lagu).first()
    if not data:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")
    return data

# ❌ Hapus prapemrosesan berdasarkan ID lagu
def delete_prapemrosesan(id_lagu: int, db: Session):
    data = db.query(Prapemrosesan).filter(Prapemrosesan.id_lagu == id_lagu).first()
    if not data:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")
    db.delete(data)
    db.commit()
    return {"message": f"Data prapemrosesan untuk lagu ID {id_lagu} berhasil dihapus"}


def update_prapemrosesan(id_lagu: int, update_data: dict, db: Session):
    data = db.query(Prapemrosesan).filter(Prapemrosesan.id_lagu == id_lagu).first()
    if not data:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")

    for field, value in update_data.items():
        if hasattr(data, field):
            setattr(data, field, value)

    db.commit()
    db.refresh(data)
    return {"message": "Data berhasil diperbarui", "data": data}
