from controllers.LaguController import (
    get_all_lagu,
    get_lagu_by_id,
    get_lagu_by_judul,
    create_lagu,
    update_lagu,
    delete_lagu,
    get_genre_by_lagu,
    get_penyanyi_by_lagu,
    get_label_by_lagu
)
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter()
@router.get("/")
def read_lagu_list(db: Session = Depends(get_db)):
    return get_all_lagu(db)


@router.get("/{lagu_id}")
def read_lagu(lagu_id: int, db: Session = Depends(get_db)):
    lagu = get_lagu_by_id(db, lagu_id)
    if not lagu:
        raise HTTPException(status_code=404, detail="Lagu tidak ditemukan")
    return lagu

@router.get("/judul/{judul}")
def read_lagu_by_judul(judul: str, db: Session = Depends(get_db)):
    lagu = get_lagu_by_judul(db, judul)
    if not lagu:
        raise HTTPException(status_code=404, detail="Lagu tidak ditemukan")
    return lagu


@router.post("/")
def create_new_lagu(data: dict = Body(...), db: Session = Depends(get_db)):
    return create_lagu(db, data)


@router.put("/{lagu_id}")
def update_existing_lagu(lagu_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    lagu = update_lagu(db, lagu_id, data)
    if not lagu:
        raise HTTPException(status_code=404, detail="Lagu tidak ditemukan")
    return lagu


@router.delete("/{lagu_id}")
def delete_existing_lagu(lagu_id: int, db: Session = Depends(get_db)):
    lagu = delete_lagu(db, lagu_id)
    if not lagu:
        raise HTTPException(status_code=404, detail="Lagu tidak ditemukan")
    return {"message": f"Lagu dengan ID {lagu_id} berhasil dihapus"}


@router.get("/{lagu_id}/genres")
def read_genres_by_lagu(lagu_id: int, db: Session = Depends(get_db)):
    return get_genre_by_lagu(db, lagu_id)

@router.get("/{lagu_id}/penyanyis")
def read_penyanyis_by_lagu(lagu_id: int, db: Session = Depends(get_db)):
    return get_penyanyi_by_lagu(db, lagu_id)

@router.get("/{lagu_id}/labels")
def read_labels_by_lagu(lagu_id: int, db: Session = Depends(get_db)):
    return get_label_by_lagu(db, lagu_id)
