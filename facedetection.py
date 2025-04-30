import cv2
import sqlite3
import os
import numpy as np
import face_recognition
from datetime import datetime, time as dt_time
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import bcrypt
from deepface import DeepFace
import pyttsx3
import threading
import time
import schedule
from tkinter import font as tkfont

# ========== KONFIGURASI ==========
FACE_DETECTION_MODEL = "hog"  # "hog" untuk CPU, "cnn" untuk GPU
FACE_MATCHING_TOLERANCE = 0.6
TARGET_FRAME_WIDTH = 640
UPDATE_INTERVAL = 300  # 5 menit dalam detik
ROLE_OPTIONS = ['Guru', 'Siswa', 'Staf', 'Admin']
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # Password akan di-hash

# Waktu presensi
MORNING_ENTRY_TIME = dt_time(7, 30)  # 07:30 WIB masuk sekolah
AFTERNOON_EXIT_TIME = dt_time(15, 0)  # 15:00 WIB pulang sekolah
GRACE_PERIOD = 15  # toleransi 15 menit

# ========== INISIALISASI DIREKTORI ==========
def init_directories():
    os.makedirs('img', exist_ok=True)
    os.makedirs('known_faces', exist_ok=True)
    os.makedirs('screenshots', exist_ok=True)
    os.makedirs('attendance_screenshots', exist_ok=True)
    os.makedirs('attendance_records', exist_ok=True)

init_directories()

# ========== STYLE GUI ==========
class AppStyle:
    def __init__(self):
        self.bg_color = "#f0f0f0"
        self.primary_color = "#4a6fa5"
        self.secondary_color = "#166088"
        self.accent_color = "#4fc3f7"
        self.text_color = "#333333"
        self.error_color = "#d32f2f"
        self.success_color = "#388e3c"
        
        self.title_font = ("Helvetica", 16, "bold")
        self.subtitle_font = ("Helvetica", 12)
        self.normal_font = ("Helvetica", 10)
        
    def apply_style(self, root):
        root.configure(bg=self.bg_color)
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.text_color, font=self.normal_font)
        style.configure('TButton', font=self.normal_font, background=self.primary_color, foreground='white')
        style.configure('TEntry', font=self.normal_font)
        style.configure('TCombobox', font=self.normal_font)
        
        style.map('TButton',
                background=[('active', self.secondary_color), ('pressed', self.accent_color)],
                foreground=[('active', 'white')])
        
        style.configure('Accent.TButton', background=self.accent_color)
        style.configure('Error.TLabel', foreground=self.error_color)
        style.configure('Success.TLabel', foreground=self.success_color)

# ========== DATABASE ==========
class FaceDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('faces.db')
        self.admin_conn = sqlite3.connect('admin.db')
        self.attendance_conn = sqlite3.connect('attendance.db')
        self.lock = threading.Lock()
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_roles = []
        self.last_update = 0
        self.init_db()
        self.load_known_faces()

    def init_db(self):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    role TEXT,
                    image_path TEXT,
                    encoding BLOB,
                    timestamp TEXT,
                    emotion TEXT
                )
            ''')
            self.conn.commit()

            admin_cursor = self.admin_conn.cursor()
            admin_cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            
            # Hash password admin
            hashed_password = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt())
            admin_cursor.execute("INSERT OR IGNORE INTO admin (username, password) VALUES (?, ?)", 
                               (ADMIN_USERNAME, hashed_password))
            self.admin_conn.commit()
            
            # Tabel presensi
            attendance_cursor = self.attendance_conn.cursor()
            attendance_cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    date TEXT NOT NULL,
                    entry_time TEXT,
                    exit_time TEXT,
                    status TEXT
                )
            ''')
            self.attendance_conn.commit()

    def load_known_faces(self):
        with self.lock:
            self.known_face_encodings = []
            self.known_face_names = []
            self.known_face_roles = []

            cursor = self.conn.cursor()
            cursor.execute("SELECT name, role, encoding FROM faces")
            
            for name, role, encoding_blob in cursor.fetchall():
                encoding = np.frombuffer(encoding_blob, dtype=np.float64)
                self.known_face_encodings.append(encoding)
                self.known_face_names.append(name)
                self.known_face_roles.append(role)
            
            self.last_update = time.time()
            print(f"Memuat {len(self.known_face_names)} wajah yang dikenal")

    def add_face(self, name, role, face_image, face_encoding, emotion):
        with self.lock:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            img_filename = f"known_faces/{name}_{timestamp}.jpg"
            cv2.imwrite(img_filename, face_image)
            
            encoding_blob = face_encoding.tobytes()
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO faces (name, role, image_path, encoding, timestamp, emotion)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, role, img_filename, encoding_blob, timestamp, emotion))
            self.conn.commit()
            
            # Update data di memori
            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(name)
            self.known_face_roles.append(role)
            print(f"Wajah {name} berhasil didaftarkan sebagai {role}")

    def verify_admin(self, username, password):
        cursor = self.admin_conn.cursor()
        cursor.execute("SELECT password FROM admin WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if result:
            return bcrypt.checkpw(password.encode('utf-8'), result[0])
        return False
    
    def record_attendance(self, name, role, is_entry=True):
        today = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')
        
        with self.lock:
            cursor = self.attendance_conn.cursor()
            
            if is_entry:
                # Cek apakah sudah ada entry hari ini
                cursor.execute('''
                    SELECT id FROM attendance 
                    WHERE name = ? AND date = ? AND entry_time IS NOT NULL
                ''', (name, today))
                
                if cursor.fetchone() is None:
                    # Rekam presensi masuk
                    cursor.execute('''
                        INSERT INTO attendance (name, role, date, entry_time, status)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (name, role, today, current_time, 'Hadir'))
                    self.attendance_conn.commit()
                    print(f"Presensi masuk {name} dicatat pada {current_time}")
            else:
                # Rekam presensi pulang
                cursor.execute('''
                    UPDATE attendance 
                    SET exit_time = ?, status = 'Pulang'
                    WHERE name = ? AND date = ? AND exit_time IS NULL
                ''', (current_time, name, today))
                self.attendance_conn.commit()
                print(f"Presensi pulang {name} dicatat pada {current_time}")

# ========== ADMIN LOGIN GUI ==========
class AdminLoginWindow:
    def __init__(self, parent, face_db):
        self.parent = parent
        self.face_db = face_db
        self.style = AppStyle()
        self.authenticated = False
        
        self.root = tk.Toplevel(parent)
        self.root.title("Admin Login")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        self.style.apply_style(self.root)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Header Frame
        header_frame = ttk.Frame(self.root, style='TFrame')
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Logo (placeholder)
        logo_img = Image.new('RGB', (80, 80), color=self.style.primary_color)
        logo_img = ImageTk.PhotoImage(logo_img)
        logo_label = ttk.Label(header_frame, image=logo_img)
        logo_label.image = logo_img
        logo_label.pack()
        
        ttk.Label(header_frame, text="ADMIN LOGIN", font=self.style.title_font).pack(pady=10)
        
        # Form Frame
        form_frame = ttk.Frame(self.root, style='TFrame')
        form_frame.pack(fill=tk.X, padx=40, pady=10)
        
        # Username
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(form_frame, font=self.style.normal_font)
        self.username_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Password
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(form_frame, show="•", font=self.style.normal_font)
        self.password_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Error Message
        self.error_label = ttk.Label(form_frame, text="", style='Error.TLabel')
        self.error_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Button Frame
        button_frame = ttk.Frame(self.root, style='TFrame')
        button_frame.pack(fill=tk.X, padx=40, pady=20)
        
        ttk.Button(button_frame, text="LOGIN", command=self.attempt_login, 
                  style='TButton').pack(fill=tk.X, pady=5)
        
        # Footer
        ttk.Label(self.root, text="© 2023 School Attendance System", 
                 font=("Helvetica", 8), style='TLabel').pack(side=tk.BOTTOM, pady=10)
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.attempt_login())
        
    def attempt_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.error_label.config(text="Username dan password harus diisi!")
            return
            
        if self.face_db.verify_admin(username, password):
            self.authenticated = True
            self.root.destroy()
        else:
            self.error_label.config(text="Username atau password salah!")

# ========== ATTENDANCE SYSTEM ==========
class AttendanceSystem:
    def __init__(self, face_db):
        self.face_db = face_db
        self.voice_engine = pyttsx3.init()
        self.voice_engine.setProperty('rate', 150)
        self.recognized_faces = {}
        self.schedule_jobs()
        
    def schedule_jobs(self):
        # Jadwalkan pembersihan data harian
        schedule.every().day.at("00:00").do(self.clear_daily_data)
        
    def clear_daily_data(self):
        self.recognized_faces.clear()
        print("Data harian telah dibersihkan")
        
    def check_attendance_time(self, frame, name, role):
        current_time = datetime.now().time()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Cek waktu presensi masuk (07:00-07:45)
        if (self.is_time_between(current_time, 
                               dt_time(MORNING_ENTRY_TIME.hour, MORNING_ENTRY_TIME.minute - GRACE_PERIOD),
                               dt_time(MORNING_ENTRY_TIME.hour, MORNING_ENTRY_TIME.minute + GRACE_PERIOD))):
            
            if name not in self.recognized_faces or self.recognized_faces[name].date() != datetime.now().date():
                self.recognized_faces[name] = datetime.now()
                self.face_db.record_attendance(name, role, is_entry=True)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"attendance_screenshots/ENTRY_{name}_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                
                self.voice_engine.say(f"Selamat pagi {name}, selamat belajar!")
                self.voice_engine.runAndWait()
        
        # Cek waktu presensi pulang (15:00-15:15)
        elif (self.is_time_between(current_time, 
                                 dt_time(AFTERNOON_EXIT_TIME.hour, AFTERNOON_EXIT_TIME.minute),
                                 dt_time(AFTERNOON_EXIT_TIME.hour, AFTERNOON_EXIT_TIME.minute + GRACE_PERIOD))):
            
            if name in self.recognized_faces and self.recognized_faces[name].date() == datetime.now().date():
                self.face_db.record_attendance(name, role, is_entry=False)
                del self.recognized_faces[name]
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"attendance_screenshots/EXIT_{name}_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                
                self.voice_engine.say(f"Selamat jalan {name}, hati-hati di jalan!")
                self.voice_engine.runAndWait()
    
    def is_time_between(self, check_time, start_time, end_time):
        if start_time <= end_time:
            return start_time <= check_time <= end_time
        else:  # Waktu melewati tengah malam
            return start_time <= check_time or check_time <= end_time

# ========== MAIN APPLICATION ==========
class FaceRecognitionApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.style = AppStyle()
        self.face_db = FaceDatabase()
        self.attendance_system = AttendanceSystem(self.face_db)
        self.admin_mode = False
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, TARGET_FRAME_WIDTH)
        
    def run(self):
        try:
            while True:
                # Jalankan scheduled jobs
                schedule.run_pending()
                
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Deteksi wajah
                face_locations = face_recognition.face_locations(rgb_frame, model=FACE_DETECTION_MODEL)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    # Gambar kotak
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    
                    # Cocokkan dengan wajah yang dikenal
                    matches = face_recognition.compare_faces(
                        self.face_db.known_face_encodings, 
                        face_encoding, 
                        tolerance=FACE_MATCHING_TOLERANCE
                    )
                    face_distances = face_recognition.face_distance(
                        self.face_db.known_face_encodings, 
                        face_encoding
                    )
                    
                    if len(face_distances) > 0:
                        best_match_index = np.argmin(face_distances)
                        
                        if matches[best_match_index]:
                            name = self.face_db.known_face_names[best_match_index]
                            role = self.face_db.known_face_roles[best_match_index]
                            emotion = detect_emotion(frame[top:bottom, left:right])
                            
                            # Tampilkan info
                            cv2.putText(frame, name, (left, top - 10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                            cv2.putText(frame, f"{role} | {emotion}", (left, top - 40), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                            
                            # Cek waktu presensi
                            self.attendance_system.check_attendance_time(frame, name, role)
                            
                            # Simpan screenshot
                            if name not in self.attendance_system.recognized_faces:
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                cv2.imwrite(f"screenshots/{name}_{timestamp}.jpg", frame)
                        else:
                            cv2.putText(frame, "Unknown", (left, top - 10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                
                # Tampilkan instruksi
                self.display_instructions(frame)
                
                cv2.imshow("Face Recognition System", frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('a') and not self.admin_mode:
                    self.show_admin_login()
                elif key == ord('s') and self.admin_mode and face_locations:
                    self.register_new_face(frame, face_locations[0], face_encodings[0])
        
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.cleanup()
            
    def display_instructions(self, frame):
        cv2.putText(frame, "Press 'A' for Admin Login", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        if self.admin_mode:
            cv2.putText(frame, "ADMIN MODE", (frame.shape[1] - 150, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, "Press 'S' to Register Face", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Tampilkan waktu saat ini
        current_time = datetime.now().strftime('%H:%M:%S')
        cv2.putText(frame, current_time, (frame.shape[1] - 120, frame.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Tampilkan info waktu presensi
        cv2.putText(frame, f"Masuk: {MORNING_ENTRY_TIME.strftime('%H:%M')}±{GRACE_PERIOD}m", 
                   (10, frame.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, f"Pulang: {AFTERNOON_EXIT_TIME.strftime('%H:%M')}±{GRACE_PERIOD}m", 
                   (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    def show_admin_login(self):
        login_window = AdminLoginWindow(self.root, self.face_db)
        self.root.wait_window(login_window.root)
        self.admin_mode = login_window.authenticated
        
    def register_new_face(self, frame, face_location, face_encoding):
        top, right, bottom, left = face_location
        face_image = frame[top:bottom, left:right]
        emotion = detect_emotion(face_image)
        
        registration_window = RegistrationWindow(
            self.root, 
            face_image, 
            face_encoding,
            emotion
        )
        self.root.wait_window(registration_window.root)
        
        if registration_window.registration_complete:
            self.face_db.add_face(
                registration_window.name,
                registration_window.role,
                face_image,
                face_encoding,
                emotion
            )
            self.face_db.load_known_faces()
    
    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.face_db.conn.close()
        self.face_db.admin_conn.close()
        self.face_db.attendance_conn.close()
        self.attendance_system.voice_engine.stop()
        self.root.destroy()

# ========== REGISTRATION WINDOW ==========
class RegistrationWindow:
    def __init__(self, parent, face_image, face_encoding, emotion):
        self.parent = parent
        self.face_image = face_image
        self.face_encoding = face_encoding
        self.emotion = emotion
        self.style = AppStyle()
        self.registration_complete = False
        self.name = ""
        self.role = ""
        
        self.root = tk.Toplevel(parent)
        self.root.title("Register New Face")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        self.style.apply_style(self.root)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.root, style='TFrame')
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(header_frame, text="NEW REGISTRATION", 
                 font=self.style.title_font).pack()
        
        # Preview wajah
        preview_frame = ttk.Frame(self.root, style='TFrame')
        preview_frame.pack(pady=10)
        
        face_img = Image.fromarray(cv2.cvtColor(self.face_image, cv2.COLOR_BGR2RGB))
        face_img = face_img.resize((200, 200), Image.LANCZOS)
        self.face_preview = ImageTk.PhotoImage(face_img)
        
        ttk.Label(preview_frame, image=self.face_preview).pack()
        ttk.Label(preview_frame, text=f"Emotion: {self.emotion}", 
                 font=self.style.subtitle_font).pack(pady=5)
        
        # Form
        form_frame = ttk.Frame(self.root, style='TFrame')
        form_frame.pack(fill=tk.X, padx=40, pady=10)
        
        # Name
        ttk.Label(form_frame, text="Full Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(form_frame, font=self.style.normal_font)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Role
        ttk.Label(form_frame, text="Role:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.role_combobox = ttk.Combobox(
            form_frame, 
            values=ROLE_OPTIONS, 
            state="readonly",
            font=self.style.normal_font
        )
        self.role_combobox.current(0)
        self.role_combobox.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Error message
        self.error_label = ttk.Label(form_frame, text="", style='Error.TLabel')
        self.error_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.root, style='TFrame')
        button_frame.pack(fill=tk.X, padx=40, pady=20)
        
        ttk.Button(button_frame, text="REGISTER", command=self.register, 
                  style='Accent.TButton').pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="CANCEL", command=self.cancel).pack(fill=tk.X)
        
        self.root.grab_set()
    
    def register(self):
        self.name = self.name_entry.get().strip()
        self.role = self.role_combobox.get()
        
        if not self.name:
            self.error_label.config(text="Full name must be filled!")
            return
            
        self.registration_complete = True
        self.root.destroy()
    
    def cancel(self):
        self.root.destroy()

# ========== FUNGSI UTILITAS ==========
def detect_emotion(face_image):
    """Mendeteksi ekspresi wajah menggunakan DeepFace"""
    try:
        rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        result = DeepFace.analyze(rgb_image, actions=['emotion'], enforce_detection=False)
        
        if isinstance(result, list):
            result = result[0]
            
        return result['dominant_emotion'].capitalize()
    except Exception as e:
        print(f"Error deteksi ekspresi: {e}")
        return "Unknown"

if __name__ == "__main__":
    app = FaceRecognitionApp()
    app.run()