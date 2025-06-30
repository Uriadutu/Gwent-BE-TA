from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json, os

GT_FILE = "data/likes.json"
like_router = APIRouter()

class LikeRequest(BaseModel):
    keyword: str
    liked_title: str | None  # ✅ now nullable
    recommended: list[str]
    
@like_router.post("/like")
def simpan_like(req: LikeRequest):
    try:
        keyword = req.keyword.lower().strip()
        liked_title = req.liked_title.strip() if req.liked_title else None
        recommended = [judul.strip() for judul in req.recommended]

        relevan_index = -1

        # Load file GT
        if os.path.exists(GT_FILE):
            with open(GT_FILE, "r", encoding="utf-8") as f:
                gt_data = json.load(f)
        else:
            gt_data = {}

        # Jika belum ada keyword, inisialisasi
        if keyword not in gt_data:
            gt_data[keyword] = {
                "recommended": recommended,
                "relevan": {}
            }
        else:
            # Hanya update recommended jika belum ada
            if not gt_data[keyword].get("recommended"):
                gt_data[keyword]["recommended"] = recommended

        # Tambahkan relevansi jika ada liked_title
        if liked_title:
            try:
                relevan_index = recommended.index(liked_title)
                # Tambah ke dict relevan (jangan menimpa semuanya)
                gt_data[keyword]["relevan"][liked_title] = relevan_index
            except ValueError:
                relevan_index = -1  # tidak ditemukan dalam rekomendasi

        # Simpan ulang
        with open(GT_FILE, "w", encoding="utf-8") as f:
            json.dump(gt_data, f, indent=2, ensure_ascii=False)

        return {
            "message": "Berhasil disimpan",
            "index_relevan": relevan_index if relevan_index != -1 else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
