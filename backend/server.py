from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import shutil
import cv2
import numpy as np
from PIL import Image
import io
import random
from database import get_db, init_db, FreshwaterSpecies as DBFreshwaterSpecies, Classification as DBClassification

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app without a prefix
app = FastAPI(title="Sistem Klasifikasi Ikan Air Tawar Pemancingan", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Create uploads directory
# Use local uploads directory for development, /app/uploads for production
UPLOAD_DIR = Path(os.environ.get('UPLOAD_DIR', str(ROOT_DIR.parent / 'uploads')))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Define Models
class FreshwaterSpecies(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nama_umum: str
    nama_ilmiah: str
    deskripsi: str
    karakteristik: List[str]
    habitat: str
    ukuran_avg: str
    gambar_contoh: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClassificationResult(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nama_ikan: str
    tingkat_keyakinan: float
    gambar_path: str
    thumbnail_path: str
    species_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClassificationResponse(BaseModel):
    hasil_klasifikasi: str
    tingkat_keyakinan: float
    species_id: Optional[str] = None
    gambar_url: str
    thumbnail_url: str
    riwayat_id: str

class SpeciesCreate(BaseModel):
    nama_umum: str
    nama_ilmiah: str
    deskripsi: str
    karakteristik: List[str]
    habitat: str
    ukuran_avg: str
    gambar_contoh: str

# Mock CNN Model Class
class MockFreshwaterCNN:
    def __init__(self):
        self.fish_types = [
            "Nila", "Mas", "Lele", "Mujair", "Gurame", "Patin",
            "Bawal Air Tawar", "Toman", "Gabus", "Jelawat",
            "Nila Merah", "Tawes", "Sepat Siam", "Tambakan"
        ]

    def preprocess_image(self, image_bytes):
        """Simulate image preprocessing like a real CNN"""
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize to standard CNN input size
        image = image.resize((224, 224))

        # Convert to numpy array and normalize
        img_array = np.array(image) / 255.0
        return img_array

    def predict(self, image_array):
        """Mock prediction with realistic confidence scores"""
        # Simulate CNN prediction with weighted random selection
        weights = [0.20, 0.18, 0.15, 0.12, 0.10, 0.08, 0.06, 0.04, 0.03, 0.02, 0.01, 0.007, 0.002, 0.001]
        # Normalize weights to ensure they sum to 1.0
        weights = np.array(weights)
        weights = weights / weights.sum()
        selected_idx = np.random.choice(len(self.fish_types), p=weights)

        # Generate realistic confidence score (higher for common types)
        if selected_idx < 3:  # Nila, Mas, Lele - most common
            confidence = random.uniform(0.75, 0.95)
        elif selected_idx < 8:  # Common freshwater fish
            confidence = random.uniform(0.60, 0.85)
        else:  # Less common varieties
            confidence = random.uniform(0.45, 0.75)

        return self.fish_types[selected_idx], confidence

# Initialize mock model
mock_cnn = MockFreshwaterCNN()

# Helper Functions
def create_thumbnail(image_path: Path, size=(150, 150)):
    """Create thumbnail for uploaded image"""
    thumb_path = image_path.parent / f"thumb_{image_path.name}"

    with Image.open(image_path) as img:
        img.thumbnail(size, Image.Resampling.LANCZOS)
        img.save(thumb_path, "JPEG", quality=85)

    return thumb_path

def init_sample_data(db: Session):
    """Initialize sample freshwater fishing fish data"""
    existing = db.query(DBFreshwaterSpecies).count()
    if existing > 0:
        return

    sample_species = [
        {
            "id": str(uuid.uuid4()),
            "nama_umum": "Nila",
            "nama_ilmiah": "Oreochromis niloticus",
            "deskripsi": "Ikan air tawar yang populer untuk dipancing dan dibudidayakan, memiliki daging yang enak dan mudah ditangkap",
            "karakteristik": ["Tubuh pipih dan tinggi", "Warna abu-abu keperakan", "Mudah beradaptasi", "Omnivora"],
            "habitat": "Sungai, waduk, danau air tawar",
            "ukuran_avg": "20-30 cm",
            "gambar_contoh": "https://images.unsplash.com/photo-1524704654690-b56c05c78a00?w=300&h=200&fit=crop"
        },
        {
            "id": str(uuid.uuid4()),
            "nama_umum": "Mas",
            "nama_ilmiah": "Cyprinus carpio",
            "deskripsi": "Ikan mas adalah target favorit pemancing, dikenal dengan tarikannya yang kuat dan ukurannya yang besar",
            "karakteristik": ["Tubuh memanjang dengan sisik besar", "Warna keemasan atau keperakan", "Memiliki sungut", "Herbivora"],
            "habitat": "Danau, waduk, sungai tenang",
            "ukuran_avg": "30-50 cm",
            "gambar_contoh": "https://images.unsplash.com/photo-1535591273668-578e31182c4f?w=300&h=200&fit=crop"
        },
        {
            "id": str(uuid.uuid4()),
            "nama_umum": "Lele",
            "nama_ilmiah": "Clarias batrachus",
            "deskripsi": "Ikan lele sangat populer untuk dipancing di malam hari, memiliki kumis panjang sebagai sensor",
            "karakteristik": ["Tidak bersisik", "Memiliki kumis panjang", "Aktif malam hari", "Karnivora"],
            "habitat": "Sungai, rawa, kolam berlumpur",
            "ukuran_avg": "25-40 cm",
            "gambar_contoh": "https://images.unsplash.com/photo-1567603518563-7e4f63a4a145?w=300&h=200&fit=crop"
        },
        {
            "id": str(uuid.uuid4()),
            "nama_umum": "Mujair",
            "nama_ilmiah": "Oreochromis mossambicus",
            "deskripsi": "Ikan yang mudah ditangkap, cocok untuk pemancing pemula dan sering ditemukan di perairan umum",
            "karakteristik": ["Mirip nila tapi lebih kecil", "Warna hitam keabuan", "Parental care tinggi", "Omnivora"],
            "habitat": "Sungai, danau, waduk",
            "ukuran_avg": "15-25 cm",
            "gambar_contoh": "https://images.unsplash.com/photo-1535591273668-578e31182c4f?w=300&h=200&fit=crop"
        },
        {
            "id": str(uuid.uuid4()),
            "nama_umum": "Gurame",
            "nama_ilmiah": "Osphronemus goramy",
            "deskripsi": "Ikan besar yang menjadi trophy fish, memiliki tarikan kuat dan daging yang lezat",
            "karakteristik": ["Tubuh besar dan pipih", "Sirip panjang", "Pertumbuhan lambat", "Herbivora"],
            "habitat": "Danau, waduk, rawa",
            "ukuran_avg": "40-60 cm",
            "gambar_contoh": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?w=300&h=200&fit=crop"
        },
        {
            "id": str(uuid.uuid4()),
            "nama_umum": "Patin",
            "nama_ilmiah": "Pangasius hypophthalmus",
            "deskripsi": "Ikan catfish besar yang memberikan perlawanan hebat saat dipancing",
            "karakteristik": ["Tubuh besar tidak bersisik", "Memiliki sungut", "Perenang cepat", "Omnivora"],
            "habitat": "Sungai besar, waduk",
            "ukuran_avg": "50-100 cm",
            "gambar_contoh": "https://images.unsplash.com/photo-1544943910-4c1dc44aab44?w=300&h=200&fit=crop"
        },
        {
            "id": str(uuid.uuid4()),
            "nama_umum": "Bawal Air Tawar",
            "nama_ilmiah": "Colossoma macropomum",
            "deskripsi": "Ikan kuat dengan tarikan yang powerful, populer di kolam pemancingan",
            "karakteristik": ["Tubuh bulat pipih", "Warna hitam keperakan", "Gigi kuat", "Omnivora"],
            "habitat": "Danau, waduk, kolam pemancingan",
            "ukuran_avg": "30-50 cm",
            "gambar_contoh": "https://images.unsplash.com/photo-1535591273668-578e31182c4f?w=300&h=200&fit=crop"
        },
        {
            "id": str(uuid.uuid4()),
            "nama_umum": "Gabus",
            "nama_ilmiah": "Channa striata",
            "deskripsi": "Predator ganas yang menjadi target sport fishing, dikenal dengan serangannya yang agresif",
            "karakteristik": ["Kepala besar seperti ular", "Predator ganas", "Nafas dengan udara", "Karnivora"],
            "habitat": "Rawa, sungai, danau",
            "ukuran_avg": "30-60 cm",
            "gambar_contoh": "https://images.unsplash.com/photo-1520637836862-4d197d17c17a?w=300&h=200&fit=crop"
        }
    ]

    for species_data in sample_species:
        species = DBFreshwaterSpecies(**species_data)
        db.add(species)

    db.commit()

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Sistem Klasifikasi Ikan Air Tawar Pemancingan API", "status": "aktif"}

@api_router.get("/species", response_model=List[FreshwaterSpecies])
async def get_all_species(db: Session = Depends(get_db)):
    """Dapatkan semua jenis ikan air tawar"""
    species_list = db.query(DBFreshwaterSpecies).all()
    return species_list

@api_router.get("/species/{species_id}", response_model=FreshwaterSpecies)
async def get_species_detail(species_id: str, db: Session = Depends(get_db)):
    """Dapatkan detail spesies berdasarkan ID"""
    species = db.query(DBFreshwaterSpecies).filter(DBFreshwaterSpecies.id == species_id).first()
    if not species:
        raise HTTPException(status_code=404, detail="Spesies tidak ditemukan")
    return species

@api_router.post("/classify", response_model=ClassificationResponse)
async def classify_fish(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Klasifikasi gambar ikan air tawar"""
    # Validasi file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File harus berupa gambar")

    # Check file size (5MB limit)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(status_code=400, detail="Ukuran file maksimal 5MB")

    # Save uploaded file
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    # Create thumbnail
    thumb_path = create_thumbnail(file_path)

    # Preprocess and classify
    try:
        img_array = mock_cnn.preprocess_image(contents)
        predicted_type, confidence = mock_cnn.predict(img_array)

        # Find matching species in database
        species = db.query(DBFreshwaterSpecies).filter(DBFreshwaterSpecies.nama_umum == predicted_type).first()
        species_id = species.id if species else None

        # Save classification result
        classification_id = str(uuid.uuid4())
        classification = DBClassification(
            id=classification_id,
            nama_ikan=predicted_type,
            tingkat_keyakinan=confidence,
            gambar_path=str(file_path),
            thumbnail_path=str(thumb_path),
            species_id=species_id,
            created_at=datetime.now(timezone.utc)
        )

        db.add(classification)
        db.commit()

        # Return response
        return ClassificationResponse(
            hasil_klasifikasi=predicted_type,
            tingkat_keyakinan=round(confidence, 2),
            species_id=species_id,
            gambar_url=f"/uploads/{unique_filename}",
            thumbnail_url=f"/uploads/thumb_{unique_filename}",
            riwayat_id=classification_id
        )

    except Exception as e:
        # Clean up files on error
        if file_path.exists():
            file_path.unlink()
        if 'thumb_path' in locals() and thumb_path.exists():
            thumb_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error dalam klasifikasi: {str(e)}")

@api_router.get("/history", response_model=List[ClassificationResult])
async def get_classification_history(db: Session = Depends(get_db)):
    """Dapatkan riwayat klasifikasi"""
    history = db.query(DBClassification).order_by(DBClassification.created_at.desc()).limit(100).all()
    return history

@api_router.delete("/history/{classification_id}")
async def delete_classification(classification_id: str, db: Session = Depends(get_db)):
    """Hapus riwayat klasifikasi"""
    result = db.query(DBClassification).filter(DBClassification.id == classification_id).delete()
    db.commit()

    if result == 0:
        raise HTTPException(status_code=404, detail="Riwayat tidak ditemukan")

    return {"message": "Riwayat berhasil dihapus"}

@api_router.post("/species", response_model=FreshwaterSpecies)
async def create_species(species_data: SpeciesCreate, db: Session = Depends(get_db)):
    """Tambah spesies baru (admin)"""
    species_id = str(uuid.uuid4())
    species = DBFreshwaterSpecies(
        id=species_id,
        **species_data.model_dump()
    )

    db.add(species)
    db.commit()
    db.refresh(species)

    return species

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Inisialisasi Sistem Klasifikasi Ikan Air Tawar")
    init_db()  # Create tables
    db = next(get_db())
    init_sample_data(db)  # Insert sample data
    logger.info("Data sampel ikan air tawar berhasil dimuat")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Sistem Klasifikasi Ikan Air Tawar")
