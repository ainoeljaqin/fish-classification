## How to Run

### Start MySQL Container
```bash
cd /projects/fish-classification
docker-compose up -d
```

### Check MySQL Status
```bash
docker-compose ps
```

### Start Backend Server
```bash
cd /projects/fish-classification/backend
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Test API
```bash
# Check API status
curl http://localhost:8000/api/

# Get all species
curl http://localhost:8000/api/species
```

### Start Frontend
```bash
cd /projects/fish-classification/frontend
npm start
```

## Database Schema

### betta_species
- `id` VARCHAR(36) PRIMARY KEY
- `nama_umum` VARCHAR(100)
- `nama_ilmiah` VARCHAR(100)
- `deskripsi` TEXT
- `karakteristik` JSON
- `habitat` VARCHAR(200)
- `ukuran_avg` VARCHAR(50)
- `gambar_contoh` VARCHAR(500)
- `created_at` DATETIME

### classifications
- `id` VARCHAR(36) PRIMARY KEY
- `nama_ikan` VARCHAR(100)
- `tingkat_keyakinan` FLOAT
- `gambar_path` VARCHAR(500)
- `thumbnail_path` VARCHAR(500)
- `species_id` VARCHAR(36) NULLABLE
- `created_at` DATETIME

## Notes

1. **No Watermark**: The application doesn't add watermarks to images. It only creates thumbnails (150x150px).

2. **Data Migration**: Sample data is automatically inserted on first startup (5 Betta species).

3. **Connection**: Using TCP connection (`127.0.0.1:3306`) instead of socket to ensure Docker MySQL is accessible.

4. **Credentials**:
   - MySQL User: `bettauser`
   - MySQL Password: `bettapass123`
   - Root Password: `rootpassword`
   - (Change these for production!)

## Migration Complete ✓

The application has been successfully migrated from MongoDB to MySQL and is running locally.
