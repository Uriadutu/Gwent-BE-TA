from sqlalchemy.orm import Session
from models import Penyanyi, Label

# Ambil semua penyanyi
def get_all_penyanyi(db: Session):
    penyanyi_list = db.query(Penyanyi).all()
    result = []
    for p in penyanyi_list:
        result.append({
            "id": p.id,
            "nama": p.nama,
            "id_label": p.id_label,
            "nama_label": p.label.nama_label if p.label else None
        })
    return result

# Ambil penyanyi berdasarkan ID
def get_penyanyi_by_id(db: Session, penyanyi_id: int):
    p = db.query(Penyanyi).filter(Penyanyi.id == penyanyi_id).first()
    if not p:
        return None
    return {
        "id": p.id,
        "nama": p.nama,
        "id_label": p.id_label,
        "nama_label": p.label.nama_label if p.label else None
    }

# Ambil penyanyi berdasarkan nama
def get_penyanyi_by_nama(db: Session, nama: str):
    p = db.query(Penyanyi).filter(Penyanyi.nama == nama).first()
    if not p:
        return None
    return {
        "id": p.id,
        "nama": p.nama,
        "id_label": p.id_label,
        "nama_label": p.label.nama_label if p.label else None
    }

# Tambah penyanyi baru (dengan id_label)
def create_penyanyi(db: Session, data: dict):
    nama = data.get("nama")
    id_label = data.get("id_label")

    if not nama or not id_label:
        raise ValueError("Nama dan ID Label wajib diisi.")

    label = db.query(Label).filter(Label.id == id_label).first()
    if not label:
        raise ValueError(f"Label dengan ID {id_label} tidak ditemukan.")

    new_penyanyi = Penyanyi(nama=nama, id_label=id_label)
    db.add(new_penyanyi)
    db.commit()
    db.refresh(new_penyanyi)
    return new_penyanyi


# Update penyanyi
def update_penyanyi(db: Session, penyanyi_id: int, data: dict):
    penyanyi = db.query(Penyanyi).filter(Penyanyi.id == penyanyi_id).first()
    if not penyanyi:
        return None

    nama = data.get("nama")
    id_label = data.get("id_label")

    if nama:
        penyanyi.nama = nama

    if id_label:
        label = db.query(Label).filter(Label.id == id_label).first()
        if not label:
            raise ValueError(f"Label dengan ID {id_label} tidak ditemukan.")
        # Update relasi jika diperlukan

    db.commit()
    db.refresh(penyanyi)
    return penyanyi

# Hapus penyanyi
def delete_penyanyi(db: Session, penyanyi_id: int):
    penyanyi = db.query(Penyanyi).filter(Penyanyi.id == penyanyi_id).first()
    if penyanyi:
        db.delete(penyanyi)
        db.commit()
    return penyanyi

# Ambil semua lagu oleh penyanyi tertentu
def get_lagu_by_penyanyi(db: Session, penyanyi_id: int):
    penyanyi = db.query(Penyanyi).filter(Penyanyi.id == penyanyi_id).first()
    if penyanyi:
        return penyanyi.lagu_list  # relasi many-to-many
    return []
