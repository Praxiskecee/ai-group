# Dokumentasi

School attendance adalah catatan kehadiran siswa di sekolah sesuai dengan jadwal yang telah ditetapkan. Kehadiran ini mencerminkan tingkat kedisiplinan dan tanggung jawab siswa terhadap kewajiban belajar. Data attendance digunakan oleh pihak sekolah untuk memantau konsistensi siswa dalam mengikuti kegiatan belajar mengajar, serta sebagai dasar dalam memberikan tindak lanjut jika terjadi ketidakhadiran yang berulang tanpa keterangan yang jelas. 







**Cara Install** 

Yang perlu di install : 

 1. cv2 : Pengolahan gambar dan video

 2.  sqlite3 : Database lokal

 3. pathlib : Membuat, menghapus, memeriksa keberadaan file/folder.

 4. os : Operasi file/folder

 5. tkinter : Membuat antarmuka grafis 

 6. messagebox, simpledialog : Menampilkan kotak dialog pesan interaktif kepada pengguna & Meminta input dari pengguna melalui dialog pop-up

 7.  datetime, date :  mengolah data waktu dan tanggal

 8. Pillow : Manipulasi gambar

 9. numpy : Operasi matematika & array

 10. face_recognition : Deteksi & pengenalan wajah

 11. openpyxl : Baca/tulis file Excel 

 12. pyttsx3 : Text-to-Speech (output suara)

 13. pandas : Analisis data (DataFrame)


 Cara meng install package: 

 1.  Pastikan Anda sudah menginstall Python

 2. Install package menggunakan pip

    Buka terminal/command prompt dan jalankan perintah berikut:

 ~ Untuk package utama:

    pip install opencv-python sqlite3 pillow face-recognition openpyxl pyttsx3 pandas

 ~ Untuk masalah khusus:

   a. Jika Anda mengalami masalah menginstall face-recognition:

     pip install cmake

     pip install dlib

     pip install face-recognition

b. Jika Anda menggunakan Linux, mungkin perlu menginstall dependensi sistem terlebih dahulu:

      sudo apt-get install python3-tk

      sudo apt-get install libopencv-dev

   ~ Cara menginstall OS

        1. Modul os sudah termasuk dalam 
           instalasi standar Python

       2. Gunakan, import os

 3. Verifikasi instalasi 

 Anda bisa memverifikasi bahwa semua package terinstall dengan benar dengan menjalankan Python interpreter dan mencoba mengimport masing-masing package 

     import cv2
     import sqlite3
     import pathlib
     import os
     import tkinter as tk
     from PIL import Image, ImageTk
     import numpy as np
     import face_recognition
     from openpyxl import Workbook,load_workbook
     import pyttsx3
     import pandas as pd

     print("Semua package berhasil diimport!")
 
 
 
 Jika tidak ada error, berarti semua package sudah terinstall dengan benar.






#  Proses

1. Inisialisasi dan Setup Awal
    - Instal library seperti OpenCV, face_recognition, numpy, pyttsx3.
    - Buat folder dan file untuk menyimpan: Encoding wajah, Metadata pengguna, Riwayat kehadiran

2. Membuka Kamera dan Menangkap Frame
    - Akses webcam menggunakan cv2.VideoCapture().
    - Tangkap frame secara real-time untuk diproses.

3. Deteksi dan Pengenalan Wajah
     - Deteksi wajah dalam frame
     - Encode wajah yang terdeteksi
     - Bandingkan encoding wajah dengan database wajah yang sudah tersimpan.

4. Pencatatan Kehadiran Otomatis
   - Jika wajah dikenali:

         ~ Catat waktu datang jika belum tercatat.
         ~ Jika sudah pernah tercatat dan wajah tidak terdeteksi lagi → waktu pulang.
   - Hitung durasi kehadiran dari waktu datang hingga pulang.
   - Simpan data ke dalam file Excel dan database lokal.

5. Penyapa Otomatis (Text-to-Speech)
    - Setelah wajah dikenali: Sistem menyapa pengguna saat datang: “Selamat pagi, [nama]”
    - Sistem mengucapkan selamat jalan saat pulang: “Selamat jalan, [nama]”
    - Menggunakan library pyttsx3.

6. Registrasi Wajah Baru
    - Jika wajah tidak dikenali: Sistem menampilkan perintah: tekan s untuk mendaftar. Setelah ditekan, muncul form (CLI atau GUI) untuk input: Nama, Kelas, Peran.
    - Wajah diambil dan encoding disimpan ke faces.npy, metadata ke faces.json.

7. Penyimpanan Screenshot Kehadiran
    - Saat pengguna hadir dan dikenali, sistem otomatis mengambil screenshot.
    - Gambar disimpan ke folder lokal

8. Penyimpanan dan Akses Riwayat Kehadiran
    - Data kehadiran pengguna disimpan dalam: File Excel, Database lokal SQLite

9. Data Permanen
    - Encoding wajah dan metadata hanya disimpan lokal.

10. Multi-user Recognition
     - Nama pengguna muncul pada masing-masing wajah yang dikenali.



 # Cara kerja

1. Inisialisasi Sistem
 - Membuat struktur folder yang diperlukan (img, known_faces, screenshots, dll)
 - Membuat/membuka database SQLite untuk menyimpan data wajah
 - Membuat/membuka spreadsheet Excel untuk pencatatan data
 - Memuat engine text-to-speech (pyttsx3) untuk memberikan feedback suara

2. Proses Pengenalan Wajah

a.  Kamera diaktifkan dan mulai menangkap frame secara real-time

b.  Setiap frame dikonversi dari format BGR ke RGB untuk diproses oleh library face_recognition

c.  Sistem mendeteksi lokasi wajah dalam frame menggunakan face_recognition.face_locations()

d. Untuk setiap wajah yang terdeteksi:
- Ekstrak encoding wajah menggunakan face_recognition.face_encodings()
- Bandingkan dengan database wajah yang dikenal
- Jika wajah dikenali:

     ~ Tampilkan kotak hijau di sekitar wajah dengan nama dan peran (role)

     ~ Jika ini pertama kali wajah dikenali dalam sesi ini:

     ~ Catat kehadiran (log_attendance)

     ~ Simpan screenshot wajah ke folder sesuai waktu (pagi/siang)

     ~ Beri salam sesuai waktu (selamat pagi/siang/sore)

- Jika wajah tidak dikenali:

      ~ Tampilkan kotak merah dengan label "Unknown"

     ~ Tampilkan petunjuk untuk menekan 's' untuk mendaftarkan wajah baru

3. Pendaftaran Wajah Baru

- Tekan tombol 's' saat wajah tidak dikenal terdeteksi
- Sistem akan membuka window Tkinter untuk memasukkan:

     ~ Nama

     ~ Kelas

     ~ Peran (role)

- Wajah akan disimpan ke:

     ~ Folder known_faces sebagai referensi masa depan

     ~ Folder img dengan timestamp

     ~ Database SQLite

     ~ Spreadsheet Excel

- Sistem akan memuat ulang database wajah yang dikenal

4. Pencatatan Kehadiran

- Sistem mencatat waktu kedatangan pertama di hari tersebut
- Ketika wajah yang sama terdeteksi lagi:

     ~ Mencatat waktu kepulangan

     ~ Menghitung durasi kehadiran

     ~ Menyimpan data ke spreadsheet

     ~ Memberikan ucapan selamat jalan

5. Fitur Tambahan

- Text-to-Speech: Memberikan feedback suara saat wajah dikenali

- Penyimpanan Screenshot Otomatis: Menyimpan gambar wajah yang terdeteksi

- Pembagian Waktu: Screenshot pagi/siang disimpan di folder berbeda

- Backup Harian: Data kehadiran harian disimpan dalam file Excel terpisah

6. Penghentian Sistem

- Tekan tombol 'q' untuk keluar dari program
- Sistem akan menyimpan data kehadiran harian ke file Excel sebelum keluar







#  Cara Penggunaan

1. Datang ke Area Absensi
   - Pastikan wajah kamu terlihat jelas di depan kamera
   - Berdiri di jarak yang pas, tidak terlalu jauh atau terlalu dekat.

2. Jika Wajahmu Sudah Terdaftar 
     - Kamera akan otomatis mengenali wajahmu
     - Kamu sudah terabsen hadir

3. Jika Wajahmu Belum Terdaftar
     - Segera minta bantuan guru/operator untuk mendaftarkan wajahmu
     - Setelah terdaftar, wajahmu akan dikenali secara otomatis saat absensi berikutnya

4. Saat Pulang Sekolah
    - Ulangi lagi dengan menghadap ke kamera.
    -  kamu sudah terabsen pulang.
   

# riset 

1. library excel


#  testing (sebelum tes di kelas)
**kendala**
1. Masih banyak eror
2. Kurangnya akurasi 

**Tambahan ( Yang diperbaiki) :**

1. Memberi pilihan level
2. Data kehadiran dan kepulangan dimasukan dalam format excel 
3. Efek suara saat kedatangan dan kepulangan
4. Ubah jam kepulangan menjadi diatas jam 1 siang
5. Upgrade GUI


# Dokumentasi Testing 
**kendala**

1. waktu nya 
2. GUI masih bermasalah 