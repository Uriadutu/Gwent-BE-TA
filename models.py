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
# Tabel Genre
# ========================
class Genre(Base):
    __tablename__ = 'genre'
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(255), unique=True, nullable=False)

    lagu_list = relationship("Lagu", secondary="genre_lagu", back_populates="genre_list")

# ========================
# Pivot Lagu - Genre (many-to-many)
# ========================
genre_lagu_table = Table(
    'genre_lagu',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('id_lagu', Integer, ForeignKey('lagu.id', ondelete="CASCADE")),
    Column('id_genre', Integer, ForeignKey('genre.id', ondelete="CASCADE"))
)

# ========================
# Tabel Label
# ========================
class Label(Base):
    __tablename__ = 'label'
    id = Column(Integer, primary_key=True, index=True)
    nama_label = Column(String(255), unique=True, nullable=False)

    penyanyi_list = relationship("Penyanyi", back_populates="label")

# ========================
# Pivot Penyanyi - Lagu (many-to-many)
# ========================
penyanyi_lagu_table = Table(
    'penyanyi_lagu',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('id_penyanyi', Integer, ForeignKey('penyanyi.id', ondelete="CASCADE")),
    Column('id_lagu', Integer, ForeignKey('lagu.id', ondelete="CASCADE"))
)

# ========================
# Tabel Penyanyi
# ========================
class Penyanyi(Base):
    __tablename__ = 'penyanyi'
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(255), unique=True, nullable=False)
    id_label = Column(Integer, ForeignKey('label.id', ondelete="SET NULL"), nullable=True)

    label = relationship("Label", back_populates="penyanyi_list")
    lagu_list = relationship("Lagu", secondary=penyanyi_lagu_table, back_populates="penyanyi_list")

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

    genre_list = relationship("Genre", secondary=genre_lagu_table, back_populates="lagu_list")
    penyanyi_list = relationship("Penyanyi", secondary=penyanyi_lagu_table, back_populates="lagu_list")
    prapemrosesan = relationship(
        "Prapemrosesan",
        back_populates="lagu",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

# ========================
# Tabel Prapemrosesan
# ========================
class Prapemrosesan(Base):
    __tablename__ = "prapemrosesan"

    id = Column(Integer, primary_key=True, index=True)
    id_lagu = Column(Integer, ForeignKey("lagu.id", ondelete="CASCADE"), nullable=False)
    prosesing = Column(Text)

    lagu = relationship("Lagu", back_populates="prapemrosesan", passive_deletes=True)
