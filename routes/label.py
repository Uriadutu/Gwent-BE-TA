from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from controllers.LabelController import (
    get_all_label, get_label_by_id, get_label_by_nama,
    create_label, update_label, delete_label,
    get_lagu_by_label
)
from database import get_db

router = APIRouter()

@router.get("/")
def read_all_labels(db: Session = Depends(get_db)):
    return get_all_label(db)

@router.get("/{label_id}")
def read_label_by_id(label_id: int, db: Session = Depends(get_db)):
    label = get_label_by_id(db, label_id)
    if not label:
        raise HTTPException(status_code=404, detail="Label tidak ditemukan")
    return label

@router.get("/nama/{nama}")
def read_label_by_nama(nama: str, db: Session = Depends(get_db)):
    label = get_label_by_nama(db, nama)
    if not label:
        raise HTTPException(status_code=404, detail="Label tidak ditemukan")
    return label

@router.post("/")
def create_new_label(data: dict = Body(...), db: Session = Depends(get_db)):
    return create_label(db, data)

@router.put("/{label_id}")
def update_existing_label(label_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    label = update_label(db, label_id, data)
    if not label:
        raise HTTPException(status_code=404, detail="Label tidak ditemukan")
    return label

@router.delete("/{label_id}")
def delete_existing_label(label_id: int, db: Session = Depends(get_db)):
    label = delete_label(db, label_id)
    if not label:
        raise HTTPException(status_code=404, detail="Label tidak ditemukan")
    return {"message": f"Label dengan ID {label_id} berhasil dihapus"}

@router.get("/{label_id}/lagu")
def read_lagu_by_label(label_id: int, db: Session = Depends(get_db)):
    lagu_list = get_lagu_by_label(db, label_id)
    if not lagu_list:
        raise HTTPException(status_code=404, detail="Tidak ada lagu dengan label ini")
    return lagu_list
