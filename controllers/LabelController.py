from sqlalchemy.orm import Session
from models import Label

# Ambil semua label
def get_all_label(db: Session):
    return db.query(Label).all()

# Ambil label berdasarkan ID
def get_label_by_id(db: Session, label_id: int):
    return db.query(Label).filter(Label.id == label_id).first()

# Ambil label berdasarkan nama
def get_label_by_nama(db: Session, nama: str):
    return db.query(Label).filter(Label.nama_label == nama).first()

# Tambah label baru
def create_label(db: Session, data: dict):
    nama_label = data.get("nama_label")

    if not nama_label:
        raise ValueError("Nama label tidak boleh kosong.")

    new_label = Label(nama_label=nama_label)

    db.add(new_label)
    db.commit()
    db.refresh(new_label)

    return new_label

# Update label berdasarkan ID
def update_label(db: Session, label_id: int, data: dict):
    label = db.query(Label).filter(Label.id == label_id).first()
    if label:
        for key, value in data.items():
            setattr(label, key, value)
        db.commit()
        db.refresh(label)
    return label

# Hapus label berdasarkan ID
def delete_label(db: Session, label_id: int):
    label = db.query(Label).filter(Label.id == label_id).first()
    if label:
        db.delete(label)
        db.commit()
    return label

# Ambil semua lagu berdasarkan label tertentu
def get_lagu_by_label(db: Session, label_id: int):
    label = db.query(Label).filter(Label.id == label_id).first()
    if label:
        return label.lagu_list  # Mengacu pada relasi many-to-many
    return []
