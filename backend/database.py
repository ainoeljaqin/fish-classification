from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL connection
DATABASE_URL = os.environ.get('DATABASE_URL', 'mysql://root:@localhost/freshwater_fish_classification')

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class FreshwaterSpecies(Base):
    __tablename__ = "freshwater_species"

    id = Column(String(36), primary_key=True)
    nama_umum = Column(String(100), nullable=False)
    nama_ilmiah = Column(String(100), nullable=False)
    deskripsi = Column(Text, nullable=False)
    karakteristik = Column(JSON, nullable=False)  # Store as JSON array
    habitat = Column(String(200), nullable=False)
    ukuran_avg = Column(String(50), nullable=False)
    gambar_contoh = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Classification(Base):
    __tablename__ = "classifications"

    id = Column(String(36), primary_key=True)
    nama_ikan = Column(String(100), nullable=False)
    tingkat_keyakinan = Column(Float, nullable=False)
    gambar_path = Column(String(500), nullable=False)
    thumbnail_path = Column(String(500), nullable=False)
    species_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
