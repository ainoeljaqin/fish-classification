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

# CNN Model Class
class FreshwaterCNN:
    def __init__(self, model_path=None):
        self.fish_types = ["Lele", "Patin", "Nila", "Gurame"]
        self.model = None
        self.img_size = (224, 224)

        # Try to load trained model if exists
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
            logger.info(f"Model loaded from {model_path}")
        else:
            logger.warning("No trained model found. Using mock predictions.")

    def load_model(self, model_path):
        """Load trained Keras model"""
        try:
            from tensorflow import keras
            self.model = keras.models.load_model(model_path)
            logger.info("Keras model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None

    def preprocess_image(self, image_bytes):
        """Preprocess image for CNN input"""
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize to standard CNN input size
        image = image.resize(self.img_size)

        # Convert to numpy array and normalize
        img_array = np.array(image) / 255.0

        # Add batch dimension for model input
        img_array = np.expand_dims(img_array, axis=0)

        return img_array

    def predict(self, image_array):
        """Predict fish type using trained model or mock"""
        if self.model is not None:
            # Real prediction using trained model
            predictions = self.model.predict(image_array, verbose=0)
            predicted_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_idx])

            return self.fish_types[predicted_idx], confidence
        else:
            # Mock prediction for testing without trained model
            # Equal weights for all 4 fish types
            weights = [0.25, 0.25, 0.25, 0.25]
            selected_idx = np.random.choice(len(self.fish_types), p=weights)

            # Generate realistic confidence score
            confidence = random.uniform(0.65, 0.92)

            return self.fish_types[selected_idx], confidence

# Initialize CNN model
# Look for trained model in models directory
MODEL_PATH = ROOT_DIR / 'models' / 'fish_classifier.h5'
cnn_model = FreshwaterCNN(model_path=str(MODEL_PATH) if MODEL_PATH.exists() else None)

# Helper Functions
def create_thumbnail(image_path: Path, size=(150, 150)):
    """Create thumbnail for uploaded image"""
    thumb_path = image_path.parent / f"thumb_{image_path.name}"

    with Image.open(image_path) as img:
        img.thumbnail(size, Image.Resampling.LANCZOS)
        img.save(thumb_path, "JPEG", quality=85)

    return thumb_path

def init_sample_data(db: Session):
    """Initialize sample freshwater fishing fish data (4 species only)"""
    existing = db.query(DBFreshwaterSpecies).count()
    if existing > 0:
        return

    sample_species = [
        {
            "id": str(uuid.uuid4()),
            "nama_umum": "Lele",
            "nama_ilmiah": "Clarias batrachus",
            "deskripsi": "Ikan lele sangat populer untuk dipancing di malam hari, memiliki kumis panjang sebagai sensor. Ikan ini mudah dibudidayakan dan menjadi favorit pemancing pemula hingga profesional.",
            "karakteristik": ["Tidak bersisik", "Memiliki kumis panjang (barbel)", "Aktif malam hari", "Tubuh licin", "Karnivora"],
            "habitat": "Sungai, rawa, kolam berlumpur, sawah",
            "ukuran_avg": "25-40 cm (budidaya), hingga 50 cm (liar)",
            "gambar_contoh": "https://images.unsplash.com/photo-1567603518563-7e4f63a4a145?w=300&h=200&fit=crop"
        },
        {
            "id": str(uuid.uuid4()),
            "nama_umum": "Patin",
            "nama_ilmiah": "Pangasius hypophthalmus",
            "deskripsi": "Ikan catfish besar yang memberikan perlawanan hebat saat dipancing. Patin adalah ikan ekonomis tinggi dengan daging yang lezat dan pertumbuhan yang cepat.",
            "karakteristik": ["Tubuh besar tidak bersisik", "Memiliki sungut pendek", "Perenang cepat", "Warna abu-abu keperakan", "Omnivora"],
            "habitat": "Sungai besar, waduk, kolam budidaya",
            "ukuran_avg": "50-100 cm",
            "gambar_contoh": "https://images.unsplash.com/photo-1544943910-4c1dc44aab44?w=300&h=200&fit=crop"
        },
        {
            "id": str(uuid.uuid4()),
            "nama_umum": "Nila",
            "nama_ilmiah": "Oreochromis niloticus",
            "deskripsi": "Ikan air tawar yang paling populer untuk dipancing dan dibudidayakan. Nila memiliki daging yang enak, mudah ditangkap, dan sangat adaptif terhadap berbagai kondisi perairan.",
            "karakteristik": ["Tubuh pipih dan tinggi", "Warna abu-abu keperakan", "Mudah beradaptasi", "Sisik besar", "Omnivora"],
            "habitat": "Sungai, waduk, danau air tawar, kolam",
            "ukuran_avg": "20-30 cm",
            "gambar_contoh": "https://images.unsplash.com/photo-1524704654690-b56c05c78a00?w=300&h=200&fit=crop"
        },
        {
            "id": str(uuid.uuid4()),
            "nama_umum": "Gurame",
            "nama_ilmiah": "Osphronemus goramy",
            "deskripsi": "Ikan besar yang menjadi trophy fish, memiliki tarikan kuat dan daging yang sangat lezat. Gurame adalah ikan prestise dengan harga jual tinggi dan menjadi target favorit pemancing.",
            "karakteristik": ["Tubuh besar dan pipih", "Sirip panjang", "Pertumbuhan lambat", "Warna kehijauan hingga keabuan", "Herbivora"],
            "habitat": "Danau, waduk, rawa, kolam",
            "ukuran_avg": "40-60 cm",
            "gambar_contoh": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?w=300&h=200&fit=crop"
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
        img_array = cnn_model.preprocess_image(contents)
        predicted_type, confidence = cnn_model.predict(img_array)

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
    logger.info("Data sampel ikan air tawar berhasil dimuat (4 spesies: Lele, Patin, Nila, Gurame)")

    # Check if model is loaded
    if cnn_model.model is None:
        logger.warning("⚠️  PERINGATAN: Model belum di-training!")
        logger.warning("⚠️  Saat ini menggunakan prediksi random (mock mode)")
        logger.warning("⚠️  Silakan training model dulu dengan menjalankan: python train_model.py")
    else:
        logger.info("✓ Model CNN berhasil dimuat dan siap digunakan!")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Sistem Klasifikasi Ikan Air Tawar")
