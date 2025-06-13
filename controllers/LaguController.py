from sqlalchemy.orm import Session
from models import Lagu, Genre, Penyanyi, Label, Dataset

def get_all_lagu(db: Session):
    return db.query(Lagu).all()

def get_lagu_by_id(db: Session, lagu_id: int):
    return db.query(Dataset).filter(Dataset.id == lagu_id).first()

def get_lagu_by_judul(db: Session, judul: str):
    
    return db.query(Dataset).filter(Dataset.judul == judul).first()

def create_lagu(db: Session, data: dict):
    # Ekstrak data utama
    judul = data.get("judul")
    tahun_rilis = data.get("tahun_rilis")
    lirik = data.get("lirik")
    link = data.get("link")

    # Ambil ID relasional
    genre_ids = data.get("genre_ids", [])
    penyanyi_ids = data.get("penyanyi_ids", [])
    label_ids = data.get("label_ids", [])

    new_lagu = Lagu(
        judul=judul,
        tahun_rilis=tahun_rilis,
        lirik=lirik,
        link=link,
    )

    # Tambahkan relasi (jika ada)
    if genre_ids:
        new_lagu.genres = db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
    if penyanyi_ids:
        new_lagu.penyanyis = db.query(Penyanyi).filter(Penyanyi.id.in_(penyanyi_ids)).all()
    if label_ids:
        new_lagu.labels = db.query(Label).filter(Label.id.in_(label_ids)).all()

    db.add(new_lagu)
    db.commit()
    db.refresh(new_lagu)
    return new_lagu

def update_lagu(db: Session, lagu_id: int, data: dict):
    lagu = db.query(Dataset).filter(Dataset.id == lagu_id).first()
    if lagu:
        for key, value in data.items():
            setattr(lagu, key, value)
        db.commit()
        db.refresh(lagu)
    return lagu

def delete_lagu(db: Session, lagu_id: int):
    lagu = db.query(Dataset).filter(Dataset.id == lagu_id).first()
    if lagu:
        db.delete(lagu)
        db.commit()
    return lagu

def get_genre_by_lagu(db: Session, lagu_id: int):
    lagu = db.query(Lagu).filter(Lagu.id == lagu_id).first()
    if lagu:
        return lagu.genre_list
    return []

def get_penyanyi_by_lagu(db: Session, lagu_id: int):
    lagu = db.query(Lagu).filter(Lagu.id == lagu_id).first()
    if lagu:
        return lagu.penyanyis
    return []

def get_label_by_lagu(db: Session, lagu_id: int):
    lagu = db.query(Lagu).filter(Lagu.id == lagu_id).first()
    if lagu:
        return lagu.labels
    return []
