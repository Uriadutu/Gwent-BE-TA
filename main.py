from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import lagu, genre, label, penyanyi, prapemrosesan
from rekomendasi import rekomendasi_router
from routes.like import like_router

app = FastAPI()


# Buat semua tabel
Base.metadata.create_all(bind=engine)

# Register routes
app.include_router(prapemrosesan.router)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(lagu.router, prefix="/lagu", tags=["Lagu"])
app.include_router(genre.router, prefix="/genres", tags=["Genre"])
app.include_router(rekomendasi_router, tags=["Rekomendasi"])
app.include_router(label.router, prefix="/label", tags=["Label"])
app.include_router(penyanyi.router, prefix="/penyanyi", tags=["Penyanyi"])
app.include_router(prapemrosesan.router, prefix="/prapemrosesan", tags=["Prapemrosesan"])
app.include_router(like_router)
