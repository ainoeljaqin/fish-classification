# Panduan Training Model CNN

Panduan lengkap untuk training model CNN klasifikasi ikan air tawar (Lele, Patin, Nila, Gurame).

## 📁 Struktur Dataset

Siapkan dataset dengan struktur folder seperti ini:

```
dataset/
├── train/
│   ├── Lele/
│   │   ├── lele_001.jpg
│   │   ├── lele_002.jpg
│   │   └── ... (minimal 100-200 gambar per kelas)
│   ├── Patin/
│   │   ├── patin_001.jpg
│   │   └── ...
│   ├── Nila/
│   │   ├── nila_001.jpg
│   │   └── ...
│   └── Gurame/
│       ├── gurame_001.jpg
│       └── ...
└── validation/
    ├── Lele/
    │   └── ... (20-30% dari jumlah training data)
    ├── Patin/
    ├── Nila/
    └── Gurame/
```

## 📸 Tips Mengumpulkan Dataset

### 1. Jumlah Data yang Disarankan

**Minimum (untuk transfer learning):**
- Training: 100-200 gambar per kelas
- Validation: 20-50 gambar per kelas
- **Total minimal: 480-1000 gambar**

**Ideal (untuk hasil terbaik):**
- Training: 500-1000 gambar per kelas
- Validation: 100-200 gambar per kelas
- **Total ideal: 2400-4800 gambar**

### 2. Kualitas Gambar

✅ **Yang Baik:**
- Resolusi minimal 224x224 pixel (lebih besar lebih baik)
- Fokus pada ikan, bukan background
- Berbagai sudut pandang (atas, samping, miring)
- Berbagai kondisi pencahayaan
- Ikan dalam kondisi hidup dan segar

❌ **Yang Harus Dihindari:**
- Gambar blur atau tidak fokus
- Resolusi terlalu rendah
- Ikan terlalu kecil di frame
- Background mendominasi
- Gambar duplikat

### 3. Variasi Data

Untuk setiap jenis ikan, kumpulkan gambar dengan variasi:
- **Ukuran ikan**: kecil, sedang, besar
- **Kondisi**: segar, hidup di air, di tangan, di ember
- **Pencahayaan**: outdoor, indoor, berbagai waktu
- **Angle**: atas, samping, diagonal
- **Background**: berbagai latar belakang

### 4. Sumber Dataset

Anda bisa mengumpulkan dataset dari:
- **Foto sendiri** (paling baik - kondisi real)
- **Google Images** (download bulk)
- **Kaggle Datasets**
- **iNaturalist**
- **Fish datasets** yang sudah tersedia online
- **Video frames** (ekstrak frame dari video)

## 🔧 Instalasi Dependencies

### 1. Install Python Dependencies untuk Training

```bash
# Pastikan Anda di root directory project
cd /projects/fish-classification

# Install dependencies untuk training
pip install -r requirements-training.txt
```

### 2. Verifikasi TensorFlow Installation

```bash
python -c "import tensorflow as tf; print(f'TensorFlow version: {tf.__version__}')"
python -c "import tensorflow as tf; print(f'GPU Available: {len(tf.config.list_physical_devices(\"GPU\")) > 0}')"
```

## 🚀 Cara Training Model

### 1. Siapkan Dataset

Letakkan semua gambar ikan di folder yang sesuai:

```bash
# Contoh struktur yang sudah benar
dataset/train/Lele/     <- 150 gambar lele
dataset/train/Patin/    <- 150 gambar patin
dataset/train/Nila/     <- 150 gambar nila
dataset/train/Gurame/   <- 150 gambar gurame

dataset/validation/Lele/   <- 30 gambar lele
dataset/validation/Patin/  <- 30 gambar patin
dataset/validation/Nila/   <- 30 gambar nila
dataset/validation/Gurame/ <- 30 gambar gurame
```

### 2. Jalankan Training Script

```bash
# Jalankan script training
python train_model.py
```

Script akan:
1. **Check dataset** - memverifikasi dataset Anda
2. **Tanya konfirmasi** - apakah Anda ingin lanjut training
3. **Pilih metode**:
   - **Option 1 (Recommended)**: Transfer Learning dengan MobileNetV2
     - Lebih cepat (20-30 menit)
     - Akurasi lebih tinggi dengan data lebih sedikit
     - Cocok untuk dataset 100-500 gambar per kelas

   - **Option 2**: CNN from Scratch
     - Membutuhkan waktu lebih lama (1-3 jam)
     - Membutuhkan lebih banyak data (500+ per kelas)
     - Lebih fleksibel tapi butuh tuning

4. **Training** - proses training dimulai
5. **Simpan model** - model terbaik disimpan otomatis

### 3. Monitor Training

Selama training, Anda akan melihat:
```
Epoch 1/50
48/48 [==============================] - 23s 481ms/step - loss: 1.3862 - accuracy: 0.2500 - val_loss: 1.3458 - val_accuracy: 0.3125
Epoch 2/50
48/48 [==============================] - 21s 438ms/step - loss: 1.2156 - accuracy: 0.4583 - val_loss: 1.1234 - val_accuracy: 0.5625
...
```

**Metrics yang penting:**
- `accuracy`: akurasi training (target: > 0.90)
- `val_accuracy`: akurasi validation (target: > 0.85)
- `loss`: error training (target: < 0.3)
- `val_loss`: error validation (target: < 0.5)

## 📊 Hasil Training

Setelah training selesai:

### 1. Model File
Model akan tersimpan di:
```
backend/models/fish_classifier.h5
```

### 2. Training Plots
Grafik training history akan tersimpan di:
```
training_plots/training_history_YYYYMMDD_HHMMSS.png
```

Grafik ini menampilkan:
- Akurasi training vs validation
- Loss training vs validation

### 3. Output Console
```
==============================================================
TRAINING COMPLETED
==============================================================
Final Training Accuracy: 0.9583
Final Validation Accuracy: 0.9062
Final Training Loss: 0.1234
Final Validation Loss: 0.2845

Model saved to: backend/models/fish_classifier.h5
```

## 🎯 Evaluasi Model

### Metrik yang Baik

**Untuk Transfer Learning (MobileNetV2):**
- Training Accuracy: 90-98%
- Validation Accuracy: 85-95%
- Gap < 5% (tidak overfitting)

**Untuk CNN from Scratch:**
- Training Accuracy: 85-95%
- Validation Accuracy: 80-90%
- Gap < 10%

### Masalah Umum

#### 1. Overfitting
**Gejala:** Training accuracy tinggi (>95%) tapi validation accuracy rendah (<70%)

**Solusi:**
- Tambah lebih banyak data training
- Tambah dropout layers
- Gunakan data augmentation lebih agresif
- Kurangi complexity model

#### 2. Underfitting
**Gejala:** Training dan validation accuracy keduanya rendah (<70%)

**Solusi:**
- Train lebih lama (tambah epochs)
- Gunakan model yang lebih kompleks
- Cek kualitas dataset
- Pastikan gambar tidak terlalu bervariasi

#### 3. Validation Accuracy Tidak Stabil
**Gejala:** Validation accuracy naik-turun drastis

**Solusi:**
- Tambah data validation
- Kurangi learning rate
- Gunakan batch size yang lebih besar

## 🔄 Menggunakan Model di Backend

### 1. Restart Backend Server

Setelah training selesai, restart backend:

```bash
# Stop backend (Ctrl+C)

# Start backend lagi
cd /projects/fish-classification/backend
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Backend akan otomatis detect dan load model:
```
INFO:     Inisialisasi Sistem Klasifikasi Ikan Air Tawar
INFO:     Model loaded from backend/models/fish_classifier.h5
INFO:     Keras model loaded successfully
INFO:     ✓ Model CNN berhasil dimuat dan siap digunakan!
```

### 2. Test Model

Upload gambar ikan melalui:
- Frontend web interface: http://localhost:3000/classify
- API endpoint: POST http://localhost:8000/api/classify

## 🔁 Re-training Model

Jika Anda ingin training ulang dengan data baru:

### 1. Tambah Data Baru
```bash
# Tambah gambar baru ke dataset
dataset/train/Lele/     <- tambah lebih banyak gambar
dataset/train/Patin/
...
```

### 2. Backup Model Lama (Opsional)
```bash
cp backend/models/fish_classifier.h5 backend/models/fish_classifier_backup_$(date +%Y%m%d).h5
```

### 3. Training Ulang
```bash
python train_model.py
```

Model baru akan overwrite model lama di `backend/models/fish_classifier.h5`

## 🛠️ Fine-tuning untuk Akurasi Lebih Tinggi

Jika akurasi model masih kurang memuaskan:

### 1. Data Augmentation
Edit `train_model.py` di bagian `ImageDataGenerator`:
```python
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=30,      # <- tingkatkan dari 20
    width_shift_range=0.3,  # <- tingkatkan dari 0.2
    height_shift_range=0.3,
    shear_range=0.3,
    zoom_range=0.3,
    horizontal_flip=True,
    brightness_range=[0.8, 1.2],  # <- tambahkan brightness
    fill_mode='nearest'
)
```

### 2. Hyperparameter Tuning
Edit konfigurasi di `train_model.py`:
```python
BATCH_SIZE = 16      # <- turunkan jika out of memory
EPOCHS = 100         # <- naikkan jika belum converge
learning_rate=0.0001 # <- turunkan untuk training yang lebih halus
```

### 3. Unfreeze Base Model Layers
Untuk transfer learning, Anda bisa unfreeze beberapa layer:
```python
# Unfreeze top layers dari MobileNetV2
base_model.trainable = True
for layer in base_model.layers[:-20]:
    layer.trainable = False
```

## 📝 Tips & Best Practices

1. **Start Small**: Mulai dengan dataset kecil (50-100 gambar per kelas) untuk test pipeline
2. **Use Transfer Learning**: Lebih cepat dan akurat untuk dataset kecil-menengah
3. **Monitor Closely**: Perhatikan training plots untuk detect overfitting
4. **Validate on Real Data**: Test model dengan foto real dari kolam/sungai
5. **Iterative Improvement**: Training → Evaluate → Collect More Data → Re-train

## 🆘 Troubleshooting

### Error: "No module named 'tensorflow'"
```bash
pip install tensorflow==2.15.0
```

### Error: "Out of Memory (OOM)"
Kurangi `BATCH_SIZE` di `train_model.py`:
```python
BATCH_SIZE = 8  # atau bahkan 4
```

### Error: "No data found in dataset"
Pastikan:
1. Folder dataset ada: `ls -la dataset/train/`
2. Ada gambar di dalam folder: `ls -la dataset/train/Lele/`
3. Format file benar: `.jpg`, `.jpeg`, atau `.png`

### Training Sangat Lambat
Jika tidak ada GPU:
- Training bisa 10-20x lebih lambat
- Kurangi EPOCHS menjadi 20-30
- Gunakan transfer learning (lebih cepat)

## 📚 Resources

- [TensorFlow Documentation](https://www.tensorflow.org/tutorials)
- [Keras Transfer Learning Guide](https://keras.io/guides/transfer_learning/)
- [Image Classification Best Practices](https://www.tensorflow.org/tutorials/images/classification)

---

**Good luck dengan training model Anda! 🐟🎣**
