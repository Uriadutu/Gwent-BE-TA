from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from controllers.PraPemrosesanController import (
    proses_dan_simpan_prapemrosesan,
    get_all_prapemrosesan,
    get_prapemrosesan_by_id,
    delete_prapemrosesan,
    update_prapemrosesan
)

router = APIRouter(prefix="/prapemroses", tags=["Prapemrosesan"])

@router.post("/{id_lagu}")
def buat_pra_data(id_lagu: int, db: Session = Depends(get_db)):
    return proses_dan_simpan_prapemrosesan(id_lagu, db)

@router.get("/")
def semua_data_prapemrosesan(db: Session = Depends(get_db)):
    return get_all_prapemrosesan(db)

@router.get("/{id_lagu}")
def satu_data_prapemrosesan(id_lagu: int, db: Session = Depends(get_db)):
    return get_prapemrosesan_by_id(id_lagu, db)

@router.delete("/{id_lagu}")
def hapus_data_prapemrosesan(id_lagu: int, db: Session = Depends(get_db)):
    return delete_prapemrosesan(id_lagu, db)

@router.put("/{id_lagu}")
def update_prapemroses_handler(id_lagu: int, payload: dict, db: Session = Depends(get_db)):
    return update_prapemrosesan(id_lagu, payload, db)
