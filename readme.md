# Dokumentasi Cara Install
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






# Dokumentasi Proses

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



# Dokumentasi Cara Penggunaan

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
   




