import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { Separator } from "./components/ui/separator";
import { toast, Toaster } from "sonner";
import { Upload, Fish, History, Database, Camera, Trash2, Eye } from "lucide-react";
import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Navigation Component
const Navigation = () => {
  const location = useLocation();
  
  const navItems = [
    { path: "/", label: "Beranda", icon: Fish },
    { path: "/classify", label: "Klasifikasi", icon: Camera },
    { path: "/database", label: "Database Ikan", icon: Database },
    { path: "/history", label: "Riwayat", icon: History }
  ];

  return (
    <nav className="bg-gradient-to-r from-emerald-600 to-teal-700 shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center space-x-2 text-white font-bold text-xl">
              <Fish className="h-8 w-8" />
              <span>FishID Pemancingan</span>
            </Link>
            
            <div className="hidden md:flex space-x-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    location.pathname === item.path
                      ? "bg-white/20 text-white"
                      : "text-white/80 hover:bg-white/10 hover:text-white"
                  }`}
                >
                  <item.icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

// Home Page Component
const HomePage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-emerald-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              Sistem Klasifikasi
              <span className="block text-emerald-100">Ikan Air Tawar Pemancingan</span>
            </h1>
            <p className="text-xl text-emerald-100 mb-8 max-w-3xl mx-auto">
              Identifikasi jenis ikan air tawar dengan teknologi CNN (Convolutional Neural Network).
              Upload foto ikan hasil pancingan Anda dan dapatkan hasil klasifikasi yang akurat dalam hitungan detik.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/classify">
                <Button size="lg" className="bg-white text-emerald-600 hover:bg-emerald-50 px-8 py-3 text-lg">
                  <Camera className="mr-2 h-5 w-5" />
                  Mulai Klasifikasi
                </Button>
              </Link>
              <Link to="/database">
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10 px-8 py-3 text-lg">
                  <Database className="mr-2 h-5 w-5" />
                  Lihat Database
                </Button>
              </Link>
            </div>
          </div>
        </div>
        
        {/* Decorative waves */}
        <div className="absolute bottom-0 left-0 right-0 pointer-events-none">
          <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg" className="pointer-events-none">
            <path d="M0 120L1440 120L1440 0C1200 40 960 60 720 45C480 30 240 -15 0 0L0 120Z" fill="rgb(248 250 252)" />
          </svg>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Fitur Unggulan</h2>
          <p className="text-xl text-gray-600">Teknologi terdepan untuk klasifikasi ikan air tawar</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="h-12 w-12 bg-emerald-100 rounded-lg flex items-center justify-center mb-4">
                <Camera className="h-6 w-6 text-emerald-600" />
              </div>
              <CardTitle>Klasifikasi Akurat</CardTitle>
              <CardDescription>
                Menggunakan model CNN yang telah dilatih untuk mengenali berbagai jenis ikan air tawar pemancingan dengan tingkat akurasi tinggi
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="h-12 w-12 bg-teal-100 rounded-lg flex items-center justify-center mb-4">
                <Database className="h-6 w-6 text-teal-600" />
              </div>
              <CardTitle>Database Lengkap</CardTitle>
              <CardDescription>
                Koleksi informasi lengkap tentang berbagai jenis ikan air tawar termasuk karakteristik dan habitat
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="h-12 w-12 bg-cyan-100 rounded-lg flex items-center justify-center mb-4">
                <History className="h-6 w-6 text-cyan-600" />
              </div>
              <CardTitle>Riwayat Klasifikasi</CardTitle>
              <CardDescription>
                Simpan dan kelola riwayat hasil klasifikasi untuk referensi dan analisis lebih lanjut
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </div>
    </div>
  );
};

// Classification Page Component
const ClassificationPage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleFileSelect = (file) => {
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
      setResult(null);
    } else {
      toast.error("Silakan pilih file gambar (JPG, PNG, WebP)");
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleClassify = async () => {
    if (!selectedFile) {
      toast.error("Silakan pilih gambar terlebih dahulu");
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${API}/classify`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setResult(response.data);
      toast.success("Klasifikasi berhasil!");
    } catch (error) {
      console.error('Classification error:', error);
      toast.error(error.response?.data?.detail || "Terjadi kesalahan saat klasifikasi");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-emerald-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Klasifikasi Ikan Air Tawar</h1>
          <p className="text-xl text-gray-600">Upload foto ikan air tawar untuk mendapatkan hasil klasifikasi</p>
        </div>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Upload Gambar</CardTitle>
            <CardDescription>
              Pilih gambar ikan air tawar (maksimal 5MB). Format yang didukung: JPG, PNG, WebP
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-emerald-500 transition-colors cursor-pointer"
              onClick={() => document.getElementById('file-input').click()}
            >
              {preview ? (
                <div className="space-y-4">
                  <img src={preview} alt="Preview" className="max-w-xs mx-auto rounded-lg shadow-md" />
                  <p className="text-sm text-gray-600">Klik untuk mengganti gambar</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <Upload className="h-12 w-12 text-gray-400 mx-auto" />
                  <div>
                    <p className="text-lg font-medium text-gray-900">Drag & drop gambar di sini</p>
                    <p className="text-sm text-gray-600">atau klik untuk memilih file</p>
                  </div>
                </div>
              )}
            </div>
            
            <input
              id="file-input"
              type="file"
              accept="image/*"
              onChange={(e) => handleFileSelect(e.target.files[0])}
              className="hidden"
            />

            {selectedFile && (
              <div className="mt-6 flex justify-center">
                <Button
                  onClick={handleClassify}
                  disabled={isLoading}
                  className="bg-emerald-600 hover:bg-emerald-700 px-8"
                >
                  {isLoading ? "Mengklasifikasi..." : "Klasifikasi Sekarang"}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {result && (
          <Card className="border-emerald-200 bg-emerald-50">
            <CardHeader>
              <CardTitle className="text-emerald-800">Hasil Klasifikasi</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <img
                    src={`${BACKEND_URL}${result.thumbnail_url}`}
                    alt="Gambar yang diklasifikasi"
                    className="w-full rounded-lg shadow-md"
                  />
                </div>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-2xl font-bold text-emerald-800 mb-2">
                      {result.hasil_klasifikasi}
                    </h3>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-600">Tingkat Keyakinan:</span>
                      <Badge variant="secondary" className="bg-emerald-100 text-emerald-800">
                        {(result.tingkat_keyakinan * 100).toFixed(1)}%
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-emerald-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${result.tingkat_keyakinan * 100}%` }}
                    ></div>
                  </div>
                  
                  {result.species_id && (
                    <Link to={`/database`}>
                      <Button variant="outline" className="border-emerald-600 text-emerald-600 hover:bg-emerald-50">
                        <Eye className="mr-2 h-4 w-4" />
                        Lihat Detail Spesies
                      </Button>
                    </Link>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

// Database Page Component
const DatabasePage = () => {
  const [species, setSpecies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSpecies();
  }, []);

  const fetchSpecies = async () => {
    try {
      const response = await axios.get(`${API}/species`);
      setSpecies(response.data);
    } catch (error) {
      console.error('Error fetching species:', error);
      toast.error("Gagal memuat database ikan");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-emerald-50 py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse space-y-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-gray-200 h-32 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-emerald-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Database Ikan Air Tawar</h1>
          <p className="text-xl text-gray-600">Koleksi lengkap jenis-jenis ikan air tawar pemancingan</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {species.map((fish) => (
            <Card key={fish.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <img
                  src={fish.gambar_contoh}
                  alt={fish.nama_umum}
                  className="w-full h-48 object-cover rounded-lg mb-4"
                />
                <CardTitle className="text-xl">{fish.nama_umum}</CardTitle>
                <CardDescription className="italic text-sm">
                  {fish.nama_ilmiah}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 mb-4 line-clamp-3">{fish.deskripsi}</p>
                
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="font-medium">Habitat:</span> {fish.habitat}
                  </div>
                  <div>
                    <span className="font-medium">Ukuran:</span> {fish.ukuran_avg}
                  </div>
                </div>

                <Separator className="my-3" />
                
                <div>
                  <span className="font-medium text-sm">Karakteristik:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {fish.karakteristik.map((char, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {char}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

// History Page Component
const HistoryPage = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API}/history`);
      setHistory(response.data);
    } catch (error) {
      console.error('Error fetching history:', error);
      toast.error("Gagal memuat riwayat klasifikasi");
    } finally {
      setLoading(false);
    }
  };

  const deleteHistory = async (id) => {
    try {
      await axios.delete(`${API}/history/${id}`);
      setHistory(history.filter(item => item.id !== id));
      toast.success("Riwayat berhasil dihapus");
    } catch (error) {
      console.error('Error deleting history:', error);
      toast.error("Gagal menghapus riwayat");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-emerald-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="bg-gray-200 h-24 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-emerald-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Riwayat Klasifikasi</h1>
          <p className="text-xl text-gray-600">Hasil klasifikasi sebelumnya</p>
        </div>

        {history.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <History className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">Belum ada riwayat klasifikasi</p>
              <Link to="/classify" className="mt-4 inline-block">
                <Button>Mulai Klasifikasi</Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {history.map((item) => (
              <Card key={item.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center gap-4">
                    <img
                      src={`${BACKEND_URL}/uploads/thumb_${item.thumbnail_path.split('/').pop()}`}
                      alt={item.nama_ikan}
                      className="w-16 h-16 object-cover rounded-lg"
                    />
                    
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900">{item.nama_ikan}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="secondary" className="bg-emerald-100 text-emerald-800">
                          {(item.tingkat_keyakinan * 100).toFixed(1)}%
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {new Date(item.created_at).toLocaleDateString('id-ID', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </span>
                      </div>
                    </div>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteHistory(item.id)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Navigation />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/classify" element={<ClassificationPage />} />
          <Route path="/database" element={<DatabasePage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
        <Toaster position="top-right" />
      </BrowserRouter>
    </div>
  );
}

export default App;