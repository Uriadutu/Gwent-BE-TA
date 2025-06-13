from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# ========================
# Tabel Dataset (sementara tidak ada relasi ke tabel lain)
# ========================
class Dataset(Base):
    __tablename__ = "dataset"
    id = Column(Integer, primary_key=True, index=True)
    judul = Column(String(255))
    penyanyi = Column(String(255))
    tahun_rilis = Column(String(255))
    label = Column(String(255))
    genre = Column(String(255))
    lirik = Column(Text)
    link = Column(Text)

# ========================
# Tabel Pivot Lagu - Genre
# ========================
genre_lagu_table = Table(
    'genre_lagu',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('id_lagu', Integer, ForeignKey('lagu.id')),
    Column('id_genre', Integer, ForeignKey('genre.id'))
)

# ================================
# Tabel Pivot Lagu - Penyanyi - Label
# ================================
lagu_penyanyi_label_table = Table(
    'lagu_penyanyi_label',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('id_lagu', Integer, ForeignKey('lagu.id')),
    Column('id_penyanyi', Integer, ForeignKey('penyanyi.id')),
    Column('id_label', Integer, ForeignKey('label.id'))
)

# ========================
# Tabel Genre
# ========================
class Genre(Base):
    __tablename__ = 'genre'
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(255), unique=True, nullable=False)

    lagu_list = relationship("Lagu", secondary=genre_lagu_table, back_populates="genre_list", overlaps="genre_list")

# ========================
# Tabel Penyanyi
# ========================
class Penyanyi(Base):
    __tablename__ = 'penyanyi'
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(255), unique=True, nullable=False)

    lagu_list = relationship("Lagu", secondary=lagu_penyanyi_label_table, back_populates="penyanyi_list", overlaps="penyanyi_list,label_list")

# ========================
# Tabel Label
# ========================
class Label(Base):
    __tablename__ = 'label'
    id = Column(Integer, primary_key=True, index=True)
    nama_label = Column(String(255), unique=True, nullable=False)

    lagu_list = relationship("Lagu", secondary=lagu_penyanyi_label_table, back_populates="label_list", overlaps="penyanyi_list,label_list")

# ========================
# Tabel Lagu
# ========================
class Lagu(Base):
    __tablename__ = 'lagu'
    id = Column(Integer, primary_key=True, index=True)
    judul = Column(String(255), nullable=False)
    tahun_rilis = Column(String(255))
    lirik = Column(Text)
    link = Column(Text)

    genre_list = relationship("Genre", secondary=genre_lagu_table, back_populates="lagu_list", overlaps="lagu_list")
    penyanyi_list = relationship("Penyanyi", secondary=lagu_penyanyi_label_table, back_populates="lagu_list", overlaps="lagu_list,label_list")
    label_list = relationship("Label", secondary=lagu_penyanyi_label_table, back_populates="lagu_list", overlaps="lagu_list,penyanyi_list")
