# 🎓 Sistem Kehadiran Sekolah Berbasis Face Recognition

**Dikembangkan oleh:** Praxis High School  
**Versi:** 1.0

---

## 📌 1. Deskripsi Singkat Sistem

Sistem ini merupakan aplikasi kehadiran digital berbasis **pengenalan wajah** yang dapat digunakan oleh siswa, guru, staf, dan admin. Dengan integrasi kamera, sistem mengenali wajah secara real-time dan mencatat waktu kehadiran maupun kepulangan, lengkap dengan deteksi **emosi** dan **pengambilan screenshot otomatis**. Hasil presensi dapat diekspor dalam format Excel yang siap digunakan sebagai laporan resmi.

---

## ✨ 2. Fitur Utama Bagi User

- ✅ Deteksi wajah otomatis menggunakan kamera
- ✅ Presensi masuk dan keluar dengan batas waktu yang ditentukan
- ✅ Deteksi emosi pengguna saat presensi
- ✅ Screenshot otomatis saat kehadiran
- ✅ Pendaftaran wajah baru untuk siswa/guru/staf
- ✅ Login aman untuk admin menggunakan bcrypt
- ✅ Ekspor laporan kehadiran dan screenshot ke file Excel
- ✅ GUI interaktif dengan shortcut keyboard
- ✅ Durasi kehadiran dihitung otomatis
- ✅ Laporan harian otomatis setiap hari

---

## ⚙️ 3. Cara Install Sistem

### 📁 A. Unduh Kode
Clone atau download project dari GitHub:
```bash
git clone https://github.com/username/sistem-kehadiran-face-recognition.git
cd sistem-kehadiran-face-recognition
```

### 🐍 B. Buat Virtual Environment *(Opsional tapi disarankan)*
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate       # Linux/macOS
```

### 📦 C. Install Library Python
Pastikan Python ≥ 3.8 sudah terinstal.

Gunakan `requirements.txt` yang tersedia:
```bash
pip install -r requirements.txt
```

### 🧱 D. (Linux/macOS) Tambahan: Install Library Sistem
**Linux (Ubuntu/Debian)**
```bash
sudo apt-get install cmake libdlib-dev libboost-all-dev python3-dev libatlas-base-dev -y
```

**macOS (dengan Homebrew)**
```bash
brew install cmake boost
```

---

## 🧭 4. Panduan Penggunaan (Langkah demi Langkah)

### 🔹 Langkah Awal
1. Jalankan program:
   ```bash
   python final_facedetections.py
   ```

2. Aplikasi akan menampilkan antarmuka GUI dengan kamera aktif.

### 🔹 Shortcut Panel dan Fungsi Tombol
| Tombol | Fungsi |
|--------|--------|
| `A` | Login sebagai Admin |
| `S` | Registrasi wajah baru (admin only) |
| `E` | Ekspor laporan presensi dan screenshot |
| `X` | Keluar dari mode admin |
| `D` | Konfirmasi kedatangan (manual) |
| `P` | Konfirmasi kepulangan (manual) |
| `Q` | Keluar dari aplikasi |

### 🔹 Proses Presensi Otomatis
1. Berdiri sejajar dengan kamera.
2. Sistem akan menampilkan nama dan emosi jika wajah dikenali.
3. Jika dalam waktu presensi masuk (05:00–09:00), akan muncul jendela konfirmasi.
4. Tekan “Konfirmasi” untuk mencatat kehadiran.
5. Sistem akan mengambil screenshot dan mengucapkan sambutan suara.

### 🔹 Proses Kepulangan Otomatis
1. Ulangi proses seperti kedatangan tetapi saat jam 13:00–16:00.
2. Sistem akan mencatat waktu pulang dan menghitung durasi kehadiran.

### 🔹 Registrasi Wajah Baru
1. Tekan `A` untuk login admin.
2. Masukkan username dan password.
3. Tekan `S` untuk mulai registrasi wajah.
4. Tempatkan wajah di depan kamera hingga terdeteksi.
5. Isi nama, pilih peran dan level (jika siswa), lalu tekan “Register”.

### 🔹 Ekspor Laporan
- Tekan `E` untuk mengekspor:
  - **Laporan kehadiran** → ke folder `excel_reports/`
  - **Laporan screenshot** → juga ke `excel_reports/`

### 🔹 Reset & Otomatisasi Harian
- Setiap jam 00:00 → data kehadiran di-reset.
- Setiap 23:59 → presensi hari itu diekspor ke Excel.
- Setiap 05:00 → laporan harian dibuat otomatis.

---

## 📁 Struktur Folder Output

```
📂 known_faces/
📂 screenshots/
    └── siswa/kelas_7/
    └── guru/
📂 attendance_screenshots/
📂 excel_reports/
📂 daily_reports/
```

---

## 🙋 FAQ
**Q: Bagaimana jika wajah tidak dikenali?**  
A: Pastikan wajah sudah terdaftar dan pencahayaan cukup.

**Q: Apakah bisa presensi dua kali dalam sehari?**  
A: Sistem akan menolak presensi ganda dan memberikan peringatan.

---

## 🚀 Siap Digunakan!
Sistem ini cocok untuk digunakan oleh sekolah, madrasah, dan lembaga pendidikan modern yang ingin menerapkan presensi berbasis teknologi AI.  
Silakan sesuaikan dan kembangkan lebih lanjut sesuai kebutuhan.

---

© 2025 Praxis High School – All Rights Reserved
