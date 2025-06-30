import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import Lagu, Genre, Label, Penyanyi
import csv

# Konfigurasi database
DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/db_suarahani"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Membaca CSV
try:
    df = pd.read_csv(
        "datasetbersih.csv",
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
            tahun_rilis = str(record.get("tahun_rilis")) if record.get("tahun_rilis") else None
            lirik = record.get("lirik")
            lirik = None if pd.isna(lirik) else str(lirik).strip()
            link = record.get("link")
            link = None if pd.isna(link) else str(link).strip()

            genre_names = [g.strip() for g in str(record.get("genre", "")).split(",") if g.strip()]
            penyanyi_names = [p.strip() for p in str(record.get("penyanyi", "")).split(",") if p.strip()]
            label_names = [l.strip() for l in str(record.get("label", "")).split(",") if l.strip()]

            if not judul or not penyanyi_names:
                print(f"[{idx}] Judul atau penyanyi kosong, dilewati.")
                continue

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

            # Penyanyi dan Label
            penyanyi_objs = []
            for i, penyanyi_name in enumerate(penyanyi_names):
                label_name = label_names[i] if i < len(label_names) else label_names[0] if label_names else "Unknown"
                
                # Label
                label = session.query(Label).filter_by(nama_label=label_name).first()
                if not label:
                    label = Label(nama_label=label_name)
                    session.add(label)
                    session.flush()

                # Penyanyi
                penyanyi = session.query(Penyanyi).filter_by(nama=penyanyi_name).first()
                if not penyanyi:
                    penyanyi = Penyanyi(nama=penyanyi_name, id_label=label.id)
                    session.add(penyanyi)
                    session.flush()
                elif not penyanyi.id_label:
                    penyanyi.id_label = label.id
                    session.flush()

                penyanyi_objs.append(penyanyi)

            # Tambah lagu baru tanpa id_penyanyi
            lagu = Lagu(
                judul=judul,
                tahun_rilis=tahun_rilis,
                lirik=lirik,
                link=link,
                genre_list=genres,
                penyanyi_list=penyanyi_objs  # hubungan many-to-many
            )
            session.add(lagu)
            session.commit()
            saved_count += 1
            print(f"[{idx}] Lagu '{judul}' berhasil disimpan.")
        except Exception as e:
            print("="*50)
            print(f"[{idx}] ❌ GAGAL menyimpan lagu")
            print(f"Judul      : {record.get('judul')}")
            print(f"Genre      : {record.get('genre')}")
            print(f"Penyanyi   : {record.get('penyanyi')}")
            print(f"Label      : {record.get('label')}")
            print(f"Tahun Rilis: {record.get('tahun_rilis')}")
            lirik = record.get('lirik')
            print(f"Lirik      : {lirik[:75]}..." if lirik else "Lirik      : -")
            print(f"Link       : {record.get('link')}")
            print(f"[ERROR]    : {e}")
            print("="*50 + "\n")
            session.rollback()

print(f"\nSelesai. {saved_count} dari {len(records)} lagu berhasil disimpan.")
