import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import Lagu, Genre, Label, Penyanyi
import csv

# Konfigurasi database
DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/db_csv"

# Setup SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Membaca CSV
try:
    df = pd.read_csv(
        "datalagu.csv",
        sep=",",
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL,
        encoding="utf-8",
        on_bad_lines="warn"
    )
except Exception as e:
    print(f"Gagal membaca file CSV: {e}")
    exit()

records = df.to_dict(orient="records")
saved_count = 0

with SessionLocal() as session:
    for idx, record in enumerate(records, start=1):
        try:
            judul = record.get("judul")
            tahun_rilis = int(record.get("tahun_rilis")) if str(record.get("tahun_rilis")).isdigit() else None
            lirik = record.get("lirik")
            link = record.get("link")

            genre_names = [g.strip() for g in str(record.get("genre", "")).split(",") if g.strip()]
            label_names = [l.strip() for l in str(record.get("label", "")).split(",") if l.strip()]
            penyanyi_names = [p.strip() for p in str(record.get("penyanyi", "")).split(",") if p.strip()]

            # Cek apakah lagu sudah ada
            existing_lagu = session.query(Lagu).filter_by(judul=judul).first()
            if existing_lagu:
                print(f"[{idx}] Lagu '{judul}' sudah ada, dilewati.")
                continue

            # Genre
            genres = []
            for name in set(genre_names):
                genre = session.query(Genre).filter_by(nama=name).first()
                if not genre:
                    genre = Genre(nama=name)
                    session.add(genre)
                    session.flush()
                genres.append(genre)

            # Label
            labels = []
            for name in set(label_names):
                label = session.query(Label).filter_by(nama_label=name).first()
                if not label:
                    label = Label(nama_label=name)
                    session.add(label)
                    session.flush()
                labels.append(label)

            # Penyanyi
            penyanyis = []
            for name in set(penyanyi_names):
                penyanyi = session.query(Penyanyi).filter_by(nama=name).first()
                if not penyanyi:
                    penyanyi = Penyanyi(nama=name)
                    session.add(penyanyi)
                    session.flush()
                penyanyis.append(penyanyi)

            # Tambah lagu baru
            lagu = Lagu(
                judul=judul,
                tahun_rilis=tahun_rilis,
                lirik=lirik,
                link=link,
                genre_list=genres,
                label_list=labels,
                penyanyi_list=penyanyis
            )
            session.add(lagu)
            session.commit()
            saved_count += 1
            print(f"[{idx}] Lagu '{judul}' berhasil disimpan.")
        except Exception as e:
            print(f"[{idx}] Gagal menyimpan lagu '{record.get('judul')}': {e}")
            session.rollback()

print(f"\nSelesai. {saved_count} dari {len(records)} lagu berhasil disimpan.")
