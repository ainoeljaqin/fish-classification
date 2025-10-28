# Dataset untuk Training Model

Folder ini digunakan untuk menyimpan dataset gambar ikan untuk training model CNN.

## Struktur Folder

```
dataset/
├── train/
│   ├── Lele/       <- Gambar ikan lele untuk training
│   ├── Patin/      <- Gambar ikan patin untuk training
│   ├── Nila/       <- Gambar ikan nila untuk training
│   └── Gurame/     <- Gambar ikan gurame untuk training
└── validation/
    ├── Lele/       <- Gambar ikan lele untuk validation
    ├── Patin/      <- Gambar ikan patin untuk validation
    ├── Nila/       <- Gambar ikan nila untuk validation
    └── Gurame/     <- Gambar ikan gurame untuk validation
```

## Cara Mengisi Dataset

### 1. Download atau Foto Gambar Ikan

Kumpulkan gambar ikan dari:
- Foto sendiri di kolam/sungai
- Google Images
- Dataset publik
- Video frames

### 2. Organize by Class

Letakkan gambar di folder yang sesuai:

```bash
# Contoh: untuk ikan lele
cp foto_lele_001.jpg dataset/train/Lele/
cp foto_lele_002.jpg dataset/train/Lele/
...

# Untuk ikan patin
cp foto_patin_001.jpg dataset/train/Patin/
...
```

### 3. Split Training dan Validation

**Ratio yang disarankan:**
- 80% untuk training
- 20% untuk validation

**Contoh:**
- Jika punya 150 gambar lele:
  - 120 gambar → `dataset/train/Lele/`
  - 30 gambar → `dataset/validation/Lele/`

## Jumlah Data yang Disarankan

### Minimum (Transfer Learning)
- **100-200 gambar per kelas**
- Total: ~480-800 gambar

### Ideal
- **500-1000 gambar per kelas**
- Total: ~2400-4000 gambar

## Format File yang Didukung

- ✅ `.jpg` / `.jpeg`
- ✅ `.png`
- ❌ `.gif` (tidak didukung)
- ❌ `.bmp` (convert ke jpg/png dulu)

## Tips Kualitas Dataset

### ✅ Good Images

1. **Fokus pada ikan**
   - Ikan mengisi 50-80% frame
   - Tidak blur
   - Pencahayaan cukup

2. **Variasi**
   - Berbagai ukuran ikan
   - Berbagai angle/sudut
   - Berbagai kondisi cahaya
   - Berbagai background

3. **Resolusi**
   - Minimal 224x224 pixel
   - Ideal: 500x500 pixel atau lebih

### ❌ Bad Images

1. **Terlalu jauh**
   - Ikan terlalu kecil di frame
   - Background mendominasi

2. **Kualitas buruk**
   - Blur/tidak fokus
   - Terlalu gelap
   - Terlalu terang (overexposed)

3. **Wrong subject**
   - Bukan ikan target
   - Multiple ikan (membingungkan)
   - Gambar duplikat

## Quick Start: Download Sample Dataset

Jika Anda ingin coba training dengan dataset sample, Anda bisa:

1. **Download from Google Images:**
```bash
# Install google-images-download (opsional)
pip install google-images-download

# Download gambar
googleimagesdownload --keywords "ikan lele" --limit 100 --output_directory dataset/train/Lele
googleimagesdownload --keywords "ikan patin" --limit 100 --output_directory dataset/train/Patin
googleimagesdownload --keywords "ikan nila" --limit 100 --output_directory dataset/train/Nila
googleimagesdownload --keywords "ikan gurame" --limit 100 --output_directory dataset/train/Gurame
```

2. **Manual download:**
   - Buka Google Images
   - Search "ikan lele"
   - Download 100-200 gambar
   - Ulangi untuk jenis ikan lainnya

3. **Split to validation:**
```bash
# Move 20% dari training ke validation (opsional - bisa pakai auto-split juga)
cd dataset
mkdir -p validation/{Lele,Patin,Nila,Gurame}

# Pindahkan 20 gambar dari tiap kelas ke validation
mv train/Lele/lele_{080..100}.jpg validation/Lele/
mv train/Patin/patin_{080..100}.jpg validation/Patin/
mv train/Nila/nila_{080..100}.jpg validation/Nila/
mv train/Gurame/gurame_{080..100}.jpg validation/Gurame/
```

## Verifikasi Dataset

Sebelum training, cek jumlah gambar:

```bash
# Check training data
echo "=== Training Data ==="
echo "Lele: $(ls -1 dataset/train/Lele/*.jpg 2>/dev/null | wc -l) gambar"
echo "Patin: $(ls -1 dataset/train/Patin/*.jpg 2>/dev/null | wc -l) gambar"
echo "Nila: $(ls -1 dataset/train/Nila/*.jpg 2>/dev/null | wc -l) gambar"
echo "Gurame: $(ls -1 dataset/train/Gurame/*.jpg 2>/dev/null | wc -l) gambar"

# Check validation data
echo -e "\n=== Validation Data ==="
echo "Lele: $(ls -1 dataset/validation/Lele/*.jpg 2>/dev/null | wc -l) gambar"
echo "Patin: $(ls -1 dataset/validation/Patin/*.jpg 2>/dev/null | wc -l) gambar"
echo "Nila: $(ls -1 dataset/validation/Nila/*.jpg 2>/dev/null | wc -l) gambar"
echo "Gurame: $(ls -1 dataset/validation/Gurame/*.jpg 2>/dev/null | wc -l) gambar"
```

## Next Steps

Setelah dataset siap:

1. ✅ Pastikan struktur folder benar
2. ✅ Verifikasi jumlah gambar cukup
3. ✅ Install dependencies: `pip install -r requirements-training.txt`
4. 🚀 Jalankan training: `python train_model.py`

---

**Happy training! 🐟**
