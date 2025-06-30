from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Lagu, Prapemrosesan
from utils.preprocessing import bersihkan_teks
from database import Base

DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/db_suarahani"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def insert_all_prapemrosesan():
    db: Session = SessionLocal()
    try:
        lagu_list = db.query(Lagu).all()
        print(f"[INFO] Jumlah lagu ditemukan: {len(lagu_list)}")

        for lagu in lagu_list:
            exists = db.query(Prapemrosesan).filter_by(id_lagu=lagu.id).first()
            if exists:
                print(f"[SKIP] Lagu ID {lagu.id} sudah ada di prapemrosesan")
                continue

            # Ambil semua nama penyanyi
            penyanyi_joined = " ".join([p.nama for p in lagu.penyanyi_list]) if lagu.penyanyi_list else ""

            # Ambil semua nama label dari penyanyi (hindari duplikat)
            label_joined = " ".join(
                sorted(
                    set(
                        p.label.nama_label
                        for p in lagu.penyanyi_list
                        if p.label and p.label.nama_label
                    )
                )
            ) if lagu.penyanyi_list else ""

            # Ambil semua nama genre
            genre_joined = " ".join([g.nama for g in lagu.genre_list]) if lagu.genre_list else ""

            # Gabungkan semua elemen ke satu string
            prosesing = " ".join([
                bersihkan_teks(str(lagu.judul or "")),
                bersihkan_teks(penyanyi_joined),
                bersihkan_teks(label_joined),
                bersihkan_teks(genre_joined),
                bersihkan_teks(str(lagu.lirik or "")),
                bersihkan_teks(str(lagu.tahun_rilis or ""))
            ]).strip()

            # Simpan ke tabel Prapemrosesan
            praproses = Prapemrosesan(
                id_lagu=lagu.id,
                prosesing=prosesing
            )
            db.add(praproses)
            print(f"[OK] Lagu ID {lagu.id} berhasil disimpan")

        db.commit()
        print("[DONE] Semua data berhasil diproses.")

    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    insert_all_prapemrosesan()
