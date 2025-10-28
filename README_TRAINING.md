# Quick Start: Training Model CNN

## 🚀 Ringkasan Cepat

Sistem klasifikasi ini menggunakan **4 jenis ikan**:
1. **Lele** (Clarias batrachus)
2. **Patin** (Pangasius hypophthalmus)
3. **Nila** (Oreochromis niloticus)
4. **Gurame** (Osphronemus goramy)

## 📁 Struktur Project

```
/projects/fish-classification/
├── backend/
│   ├── server.py              # Backend FastAPI (sudah support load model)
│   ├── database.py            # Database models
│   ├── models/                # Folder untuk model hasil training
│   │   └── fish_classifier.h5 # Model CNN (akan dibuat setelah training)
│   └── requirements.txt       # Backend dependencies
├── dataset/
│   ├── train/                 # Dataset training
│   │   ├── Lele/             # Gambar ikan lele
│   │   ├── Patin/            # Gambar ikan patin
│   │   ├── Nila/             # Gambar ikan nila
│   │   └── Gurame/           # Gambar ikan gurame
│   ├── validation/            # Dataset validation
│   │   ├── Lele/
│   │   ├── Patin/
│   │   ├── Nila/
│   │   └── Gurame/
│   └── README.md              # Panduan dataset
├── train_model.py             # Script untuk training
├── requirements-training.txt  # Dependencies untuk training
├── TRAINING_GUIDE.md          # Panduan lengkap training
└── training_plots/            # Hasil training plots (dibuat otomatis)
```

## ⚡ Quick Start (5 Langkah)

### 1️⃣ Siapkan Dataset

```bash
# Struktur folder sudah dibuat, tinggal isi dengan gambar
dataset/train/Lele/     <- Letakkan gambar lele di sini (minimal 100 gambar)
dataset/train/Patin/    <- Letakkan gambar patin di sini
dataset/train/Nila/     <- Letakkan gambar nila di sini
dataset/train/Gurame/   <- Letakkan gambar gurame di sini

# Validation (opsional, bisa pakai auto-split)
dataset/validation/     <- 20% dari training data
```

**Jumlah minimum:** 100-200 gambar per jenis ikan

### 2️⃣ Install Dependencies untuk Training

```bash
cd /projects/fish-classification

# Install TensorFlow dan dependencies
pip install -r requirements-training.txt
```

### 3️⃣ Jalankan Training

```bash
python train_model.py
```

Script akan:
- ✅ Cek dataset Anda
- ✅ Tanya konfirmasi
- ✅ Pilih metode (Transfer Learning recommended)
- ✅ Train model
- ✅ Simpan model terbaik

**Waktu training:**
- Dengan GPU: 15-30 menit
- Tanpa GPU: 1-3 jam

### 4️⃣ Restart Backend

Setelah training selesai:

```bash
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Backend akan otomatis load model:
```
INFO: ✓ Model CNN berhasil dimuat dan siap digunakan!
```

### 5️⃣ Test Klasifikasi

Upload gambar ikan melalui:
- Web: http://localhost:3000/classify
- API: POST http://localhost:8000/api/classify

## 📊 Status Saat Ini

### ✅ Yang Sudah Siap

- [x] Backend sudah support load model training
- [x] Struktur dataset sudah dibuat
- [x] Script training sudah siap
- [x] Frontend sudah diupdate untuk 4 jenis ikan
- [x] Database sudah update untuk 4 jenis ikan

### ⏳ Yang Perlu Anda Lakukan

- [ ] Kumpulkan dataset gambar ikan (100-200 per jenis)
- [ ] Install dependencies training: `pip install -r requirements-training.txt`
- [ ] Jalankan training: `python train_model.py`
- [ ] Restart backend setelah training

## 🔄 Alur Kerja

```
1. Kumpulkan Dataset
   ↓
2. Organize ke folder train/
   ↓
3. Run: python train_model.py
   ↓
4. Model tersimpan: backend/models/fish_classifier.h5
   ↓
5. Restart backend
   ↓
6. Backend auto-load model
   ↓
7. Upload gambar ikan → Klasifikasi otomatis!
```

## 🎯 Mode Operasi Backend

### Mode 1: Tanpa Model (Mock Mode) - SAAT INI
```
Status: ⚠️  Model belum di-training
Behavior: Prediksi random (untuk testing)
Akurasi: ~25% (random)
```

### Mode 2: Dengan Model Trained
```
Status: ✓ Model CNN loaded
Behavior: Prediksi menggunakan model trained
Akurasi: 85-95% (tergantung kualitas dataset)
```

## 📝 File Penting

### 1. train_model.py
Script utama untuk training. Features:
- Auto-detect dataset
- Support Transfer Learning (MobileNetV2)
- Support CNN from scratch
- Auto-save best model
- Generate training plots

### 2. TRAINING_GUIDE.md
Panduan lengkap training mencakup:
- Cara kumpulkan dataset
- Tips kualitas gambar
- Troubleshooting
- Fine-tuning
- Best practices

### 3. dataset/README.md
Panduan khusus untuk dataset:
- Struktur folder
- Format file
- Verifikasi dataset

## 🆘 Troubleshooting

### "Model belum di-training"
**Solusi:** Jalankan `python train_model.py`

### "No data found in dataset"
**Solusi:** Pastikan gambar sudah di folder `dataset/train/`

### "Module tensorflow not found"
**Solusi:** `pip install -r requirements-training.txt`

### Training terlalu lambat
**Solusi:**
- Gunakan Transfer Learning (option 1)
- Kurangi EPOCHS menjadi 20-30
- Kurangi BATCH_SIZE jika out of memory

## 📚 Dokumentasi Lengkap

- **TRAINING_GUIDE.md** - Panduan training lengkap (BACA INI!)
- **dataset/README.md** - Panduan dataset
- **how_to_run.md** - Cara menjalankan aplikasi

## 💡 Tips

1. **Start dengan Transfer Learning** (option 1) - lebih cepat dan akurat
2. **Kualitas > Kuantitas** - 100 gambar bagus > 500 gambar buruk
3. **Variasi data** - berbagai ukuran, angle, pencahayaan
4. **Monitor training** - perhatikan akurasi validation
5. **Test dengan real data** - foto ikan dari kolam/sungai asli

---

**Siap untuk training model? Baca TRAINING_GUIDE.md untuk panduan lengkap!** 🐟
