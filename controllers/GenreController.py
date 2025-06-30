from sqlalchemy.orm import Session
from models import Genre

# Ambil semua genre
def get_all_genre(db: Session):
    return db.query(Genre).all()

# Ambil genre berdasarkan ID
def get_genre_by_id(db: Session, genre_id: int):
    return db.query(Genre).filter(Genre.id == genre_id).first()

# Ambil genre berdasarkan nama
def get_genre_by_nama(db: Session, nama: str):
    return db.query(Genre).filter(Genre.nama == nama).first()

# Tambah genre baru
def create_genre(db: Session, data: dict):
    nama = data.get("nama")

    if not nama:
        raise ValueError("Nama genre tidak boleh kosong.")

    new_genre = Genre(nama=nama)

    db.add(new_genre)
    db.commit()
    db.refresh(new_genre)

    return new_genre

# Update genre berdasarkan ID
def update_genre(db: Session, genre_id: int, data: dict):
    genre = db.query(Genre).filter(Genre.id == genre_id).first()
    if genre:
        for key, value in data.items():
            setattr(genre, key, value)
        db.commit()
        db.refresh(genre)
    return genre

# Hapus genre berdasarkan ID
def delete_genre(db: Session, genre_id: int):
    genre = db.query(Genre).filter(Genre.id == genre_id).first()
    if genre:
        db.delete(genre)
        db.commit()
    return genre

# Ambil semua lagu berdasarkan genre tertentu
def get_lagu_by_genre(db: Session, genre_id: int):
    genre = db.query(Genre).filter(Genre.id == genre_id).first()
    if genre:
        return genre.lagu_list  # Mengacu pada relasi many-to-many
    return []
