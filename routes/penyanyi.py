from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from database import get_db
from controllers.PenyanyiController import (
    get_all_penyanyi,
    get_penyanyi_by_id,
    create_penyanyi,
    update_penyanyi,
    delete_penyanyi
)

router = APIRouter()

@router.get("/")
def read_penyanyi_list(db: Session = Depends(get_db)):
    return get_all_penyanyi(db)

@router.get("/{penyanyi_id}")
def read_penyanyi(penyanyi_id: int, db: Session = Depends(get_db)):
    penyanyi = get_penyanyi_by_id(db, penyanyi_id)
    if not penyanyi:
        raise HTTPException(status_code=404, detail="Penyanyi tidak ditemukan")
    return penyanyi

@router.post("/")
def create_new_penyanyi(data: dict = Body(...), db: Session = Depends(get_db)):
    return create_penyanyi(db, data)

@router.put("/{penyanyi_id}")
def update_existing_penyanyi(penyanyi_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    penyanyi = update_penyanyi(db, penyanyi_id, data)
    if not penyanyi:
        raise HTTPException(status_code=404, detail="Penyanyi tidak ditemukan")
    return penyanyi

@router.delete("/{penyanyi_id}")
def delete_existing_penyanyi(penyanyi_id: int, db: Session = Depends(get_db)):
    penyanyi = delete_penyanyi(db, penyanyi_id)
    if not penyanyi:
        raise HTTPException(status_code=404, detail="Penyanyi tidak ditemukan")
    return {"message": f"Penyanyi dengan ID {penyanyi_id} berhasil dihapus"}
