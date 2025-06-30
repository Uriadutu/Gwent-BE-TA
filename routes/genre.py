from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from controllers.GenreController import (
    get_all_genre, get_genre_by_id, get_genre_by_nama,
    create_genre, update_genre, delete_genre,
    get_lagu_by_genre
)
from database import get_db

router = APIRouter()

@router.get("/")
def read_all_genres(db: Session = Depends(get_db)):
    return get_all_genre(db)

@router.get("/{genre_id}")
def read_genre_by_id(genre_id: int, db: Session = Depends(get_db)):
    genre = get_genre_by_id(db, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre tidak ditemukan")
    return genre

@router.get("/nama/{nama}")
def read_genre_by_nama(nama: str, db: Session = Depends(get_db)):
    genre = get_genre_by_nama(db, nama)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre tidak ditemukan")
    return genre

@router.post("/")
def create_new_genre(data: dict = Body(...), db: Session = Depends(get_db)):
    return create_genre(db, data)

@router.put("/{genre_id}")
def update_existing_genre(genre_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    genre = update_genre(db, genre_id, data)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre tidak ditemukan")
    return genre

@router.delete("/{genre_id}")
def delete_existing_genre(genre_id: int, db: Session = Depends(get_db)):
    genre = delete_genre(db, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre tidak ditemukan")
    return {"message": f"Genre dengan ID {genre_id} berhasil dihapus"}

@router.get("/{genre_id}/lagu")
def read_lagu_by_genre(genre_id: int, db: Session = Depends(get_db)):
    lagu_list = get_lagu_by_genre(db, genre_id)
    if not lagu_list:
        raise HTTPException(status_code=404, detail="Tidak ada lagu dengan genre ini")
    return lagu_list
