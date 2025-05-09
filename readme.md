# Dokumentasi

**School attendance** adalah catatan kehadiran siswa di sekolah sesuai dengan jadwal yang telah ditetapkan. Kehadiran ini mencerminkan tingkat kedisiplinan dan tanggung jawab siswa terhadap kewajiban belajar. Data attendance digunakan oleh pihak sekolah untuk memantau konsistensi siswa dalam mengikuti kegiatan belajar mengajar, serta sebagai dasar dalam memberikan tindak lanjut jika terjadi ketidakhadiran yang berulang tanpa keterangan yang jelas.

---

## Cara Install

Yang perlu di-install:

1. `cv2` : Pengolahan gambar dan video
2. `sqlite3` : Database lokal
3. `pathlib` : Membuat, menghapus, memeriksa keberadaan file/folder
4. `os` : Operasi file/folder
5. `tkinter` : Antarmuka grafis
6. `messagebox`, `simpledialog` : Dialog pesan & input pengguna
7. `datetime`, `date` : Pengolahan waktu dan tanggal
8. `Pillow` : Manipulasi gambar
9. `numpy` : Operasi matematika & array
10. `face_recognition` : Deteksi & pengenalan wajah
11. `openpyxl` : Baca/tulis file Excel
12. `pyttsx3` : Text-to-Speech (output suara)
13. `pandas` : Analisis data (DataFrame)

### Cara meng-install package:

1. Pastikan Anda sudah menginstall Python.

2. Install package menggunakan pip:

   ```bash
   pip install opencv-python pillow face-recognition openpyxl pyttsx3 pandas
   ```

   Untuk masalah khusus:

   * Jika mengalami error saat install `face_recognition`:

     ```bash
     pip install cmake
     pip install dlib
     pip install face-recognition
     ```
   * Untuk pengguna Linux:

     ```bash
     sudo apt-get install python3-tk
     sudo apt-get install libopencv-dev
     ```

3. `os` dan `sqlite3` sudah termasuk dalam Python standard library.

4. Verifikasi instalasi:

   Buka Python Interpreter dan jalankan:

   ```python
   import cv2
   import sqlite3
   import pathlib
   import os
   import tkinter as tk
   from PIL import Image, ImageTk
   import numpy as np
   import face_recognition
   from openpyxl import Workbook, load_workbook
   import pyttsx3
   import pandas as pd

   print("Semua package berhasil diimport!")
   ```

Jika tidak ada error, berarti semua package sudah terinstall dengan benar.

---

## Proses

1. **Inisialisasi dan Setup Awal**

   * Instal library
   * Buat folder dan file penyimpanan wajah, metadata, riwayat

2. **Membuka Kamera dan Menangkap Frame**

   * `cv2.VideoCapture()` untuk tangkap frame secara real-time

3. **Deteksi dan Pengenalan Wajah**

   * Deteksi wajah
   * Encode wajah
   * Bandingkan encoding dengan database

4. **Pencatatan Kehadiran Otomatis**

   * Jika wajah dikenali → catat waktu datang/pulang → simpan ke Excel + DB

5. **Penyapa Otomatis (TTS)**

   * "Selamat pagi, \[nama]" / "Selamat jalan, \[nama]"

6. **Registrasi Wajah Baru**

   * Tekan `s` → isi nama, kelas, peran → simpan wajah + metadata

7. **Penyimpanan Screenshot Kehadiran**

   * Otomatis saat presensi → disimpan ke folder lokal

8. **Akses Riwayat Kehadiran**

   * Disimpan dalam Excel dan SQLite

9. **Data Permanen**

   * Disimpan lokal (tidak di-cloud)

10. **Multi-user Recognition**

    * Sistem bisa mengenali beberapa wajah sekaligus

---

## Cara Kerja

1. **Inisialisasi Sistem**

   * Buat struktur folder, buka DB, buka Excel, load TTS

2. **Pengenalan Wajah**

   * Kamera aktif → konversi BGR → RGB
   * Deteksi wajah → encode wajah → bandingkan DB
   * Jika cocok → tampilkan info, catat kehadiran, screenshot, TTS
   * Jika tidak cocok → label "Unknown" + prompt untuk registrasi

3. **Pendaftaran Wajah Baru**

   * Tekan `s` → isi form Tkinter → simpan ke DB dan folder

4. **Pencatatan Kehadiran**

   * Catat waktu datang → saat muncul kembali → catat waktu pulang → hitung durasi

5. **Fitur Tambahan**

   * TTS, screenshot otomatis, backup harian Excel

6. **Penghentian Sistem**

   * Tekan `q` → data disimpan otomatis

---

## Cara Penggunaan

1. **Datang ke Area Absensi**

   * Berdiri jelas di depan kamera

2. **Jika Wajah Sudah Terdaftar**

   * Sistem otomatis mengenali → langsung tercatat hadir

3. **Jika Belum Terdaftar**

   * Minta admin untuk registrasi

4. **Saat Pulang Sekolah**

   * Ulangi proses → sistem mencatat waktu pulang

---

