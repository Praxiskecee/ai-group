import cv2
import sqlite3
import os
import numpy as np
import face_recognition
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import hashlib
import pyttsx3

# ========== KONFIGURASI ==========
ADMIN_PASSWORD = hashlib.sha256("admin123".encode()).hexdigest()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ========== INISIALISASI DIREKTORI ==========
def init_directories():
    os.makedirs('img', exist_ok=True)
    os.makedirs('known_faces', exist_ok=True)
    os.makedirs('screenshots', exist_ok=True)
    os.makedirs('attendance_records', exist_ok=True)

init_directories()

# ========== DATABASE ==========
def init_databases():
    conn = sqlite3.connect('faces.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS faces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        employee_id TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        image_path TEXT NOT NULL,
        encoding BLOB NOT NULL,
        timestamp TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        face_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        arrival_time TEXT,
        departure_time TEXT,
        FOREIGN KEY(face_id) REFERENCES faces(id)
    )
    ''')
    
    conn.commit()
    conn.close()

init_databases()

# ========== KELAS UTILITAS ==========
class VoiceEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
    
    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

class PasswordDialog:
    def __init__(self, parent, title, mode='login'):
        self.parent = parent
        self.mode = mode
        self.password = None
        self.user_id = None
        
        self.root = tk.Toplevel(parent)
        self.root.title(title)
        self.root.geometry("300x200")
        self.root.resizable(False, False)
        
        # Widgets
        tk.Label(self.root, text="AUTHENTICATION", 
                font=('Helvetica', 12, 'bold')).pack(pady=10)
        
        tk.Label(self.root, text="ID Number:").pack()
        self.id_entry = tk.Entry(self.root)
        self.id_entry.pack(pady=5)
        
        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)
        
        if mode == 'register':
            tk.Label(self.root, text="Confirm Password:").pack()
            self.confirm_entry = tk.Entry(self.root, show="*")
            self.confirm_entry.pack(pady=5)
        
        tk.Button(self.root, text="Submit", command=self.verify).pack(pady=15)
        
        self.root.grab_set()
    
    def verify(self):
        user_id = self.id_entry.get().strip()
        password = self.password_entry.get()
        
        if not user_id:
            messagebox.showerror("Error", "ID must be entered!")
            return
            
        if self.mode == 'register':
            confirm = self.confirm_entry.get()
            if password != confirm:
                messagebox.showerror("Error", "Passwords don't match!")
                return
            if len(password) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters!")
                return
        
        self.password = password
        self.user_id = user_id
        self.root.destroy()

# ========== KELAS PRESENSI ==========
class AttendanceSystem:
    def __init__(self, parent):
        self.parent = parent
        self.voice = VoiceEngine()
        self.known_faces = []
        self.known_encodings = []
        self.known_names = []
        self.known_roles = []
        self.face_ids = []
        self.load_known_faces()
    
    def load_known_faces(self):
        conn = sqlite3.connect('faces.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, role, encoding FROM faces")
        
        self.known_faces = []
        self.known_encodings = []
        self.known_names = []
        self.known_roles = []
        self.face_ids = []
        
        for face_id, name, role, encoding_blob in cursor.fetchall():
            self.face_ids.append(face_id)
            self.known_names.append(name)
            self.known_roles.append(role)
            self.known_encodings.append(np.frombuffer(encoding_blob, dtype=np.float64))
        
        conn.close()
    
    def verify_password(self, face_id, password):
        conn = sqlite3.connect('faces.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT password_hash FROM faces WHERE id = ?", (face_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return False
            
        stored_hash = result[0]
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        
        return input_hash == stored_hash
    
    def log_attendance(self, face_id, name):
        # Verifikasi password
        password_dialog = PasswordDialog(self.parent, "Password Verification")
        self.parent.wait_window(password_dialog.root)
        
        if not password_dialog.password:
            return
            
        if not self.verify_password(face_id, password_dialog.password):
            self.voice.speak("Invalid password. Attendance not recorded.")
            return
        
        conn = sqlite3.connect('faces.db')
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # Cek apakah sudah ada presensi hari ini
        cursor.execute('''
            SELECT id, arrival_time, departure_time 
            FROM attendance 
            WHERE face_id = ? AND date = ?
        ''', (face_id, today))
        
        record = cursor.fetchone()
        
        if not record:
            # Presensi masuk
            cursor.execute('''
                INSERT INTO attendance (face_id, date, arrival_time)
                VALUES (?, ?, ?)
            ''', (face_id, today, current_time))
            
            self.voice.speak(f"Welcome {name}. Attendance recorded.")
        else:
            record_id, arrival, departure = record
            
            if not departure:
                # Presensi pulang
                cursor.execute('''
                    UPDATE attendance 
                    SET departure_time = ?
                    WHERE id = ?
                ''', (current_time, record_id))
                
                # Hitung durasi
                arrival_time = datetime.strptime(arrival, '%H:%M:%S')
                departure_time = datetime.strptime(current_time, '%H:%M:%S')
                duration = departure_time - arrival_time
                
                hours, remainder = divmod(duration.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                
                self.voice.speak(f"Goodbye {name}. Duration: {hours} hours {minutes} minutes")
            else:
                self.voice.speak(f"Welcome back {name}")
        
        conn.commit()
        conn.close()

# ========== KELAS REGISTRASI ==========
class RegistrationForm:
    def __init__(self, parent, face_image, face_encoding):
        self.parent = parent
        self.face_image = face_image
        self.face_encoding = face_encoding
        self.voice = VoiceEngine()
        self.registration_complete = False
        
        # Dialog password pertama
        self.password_dialog = PasswordDialog(parent, "Set Password", mode='register')
        parent.wait_window(self.password_dialog.root)
        
        if not self.password_dialog.password:
            return
            
        self.show_form()
    
    def show_form(self):
        self.root = tk.Toplevel(self.parent)
        self.root.title("New Registration")
        self.root.geometry("400x500")
        
        # Preview wajah
        face_img = Image.fromarray(cv2.cvtColor(self.face_image, cv2.COLOR_BGR2RGB))
        face_img = face_img.resize((200, 200), Image.LANCZOS)
        self.face_preview = ImageTk.PhotoImage(face_img)
        
        tk.Label(self.root, image=self.face_preview).pack(pady=10)
        
        # Form input
        form_frame = tk.Frame(self.root)
        form_frame.pack(pady=10)
        
        tk.Label(form_frame, text="Full Name:").grid(row=0, column=0, sticky='e', pady=5)
        self.name_entry = tk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(form_frame, text="ID Number:").grid(row=1, column=0, sticky='e', pady=5)
        self.id_entry = tk.Entry(form_frame, width=30, state='readonly')
        self.id_entry.insert(0, self.password_dialog.user_id)
        self.id_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(form_frame, text="Role:").grid(row=2, column=0, sticky='e', pady=5)
        self.role_var = tk.StringVar(value="Student")
        tk.Radiobutton(form_frame, text="Student", variable=self.role_var, value="Student").grid(row=2, column=1, sticky='w')
        tk.Radiobutton(form_frame, text="Teacher", variable=self.role_var, value="Teacher").grid(row=3, column=1, sticky='w')
        tk.Radiobutton(form_frame, text="Staff", variable=self.role_var, value="Staff").grid(row=4, column=1, sticky='w')
        
        # Tombol
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Register", command=self.register).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT)
        
        self.root.grab_set()
    
    def register(self):
        name = self.name_entry.get().strip()
        student_id = self.id_entry.get()
        role = self.role_var.get()
        password_hash = hashlib.sha256(self.password_dialog.password.encode()).hexdigest()
        
        if not name:
            messagebox.showerror("Error", "Full name must be entered!")
            return
        
        # Simpan ke database
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        face_path = os.path.join('known_faces', f'{student_id}.jpg')
        cv2.imwrite(face_path, self.face_image)
        
        encoding_blob = self.face_encoding.tobytes()
        timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            conn = sqlite3.connect('faces.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO faces (name, role, employee_id, password_hash, image_path, encoding, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, role, student_id, password_hash, face_path, encoding_blob, timestamp_str))
            conn.commit()
            conn.close()
            
            self.voice.speak(f"{name} registration successful")
            self.registration_complete = True
            self.root.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "ID already registered!")
    
    def cancel(self):
        self.root.destroy()

# ========== APLIKASI UTAMA ==========
class FaceAttendanceApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.attendance_system = AttendanceSystem(self.root)
        self.voice = VoiceEngine()
        self.cap = cv2.VideoCapture(0)
        self.admin_authenticated = False
    
    def run(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Deteksi wajah
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    # Gambar kotak
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    
                    # Cocokkan dengan wajah yang dikenal
                    matches = face_recognition.compare_faces(self.attendance_system.known_encodings, face_encoding)
                    face_distances = face_recognition.face_distance(self.attendance_system.known_encodings, face_encoding)
                    
                    if len(face_distances) > 0:
                        best_match_index = np.argmin(face_distances)
                        
                        if matches[best_match_index]:
                            name = self.attendance_system.known_names[best_match_index]
                            role = self.attendance_system.known_roles[best_match_index]
                            face_id = self.attendance_system.face_ids[best_match_index]
                            
                            # Tampilkan info
                            cv2.putText(frame, name, (left, top - 10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                            cv2.putText(frame, role, (left, top - 40), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                            
                            # Log presensi
                            self.attendance_system.log_attendance(face_id, name)
                            
                            # Simpan screenshot
                            face_img = frame[top:bottom, left:right]
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            screenshot_path = os.path.join('screenshots', f"{name}_{timestamp}.jpg")
                            cv2.imwrite(screenshot_path, face_img)
                        else:
                            cv2.putText(frame, "Unknown", (left, top - 10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                
                # Tampilkan instruksi
                cv2.putText(frame, "Press 'R' to register", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, "Press 'Q' to quit", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow("Face Attendance System", frame)
                
                key = cv2.waitKey(1)
                if key == ord('q'):
                    break
                elif key == ord('r') and face_locations:
                    self.handle_registration(frame, face_locations[0], face_encodings[0])
        
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            self.root.destroy()
    
    def handle_registration(self, frame, face_location, face_encoding):
        # Autentikasi admin
        password_dialog = PasswordDialog(self.root, "Admin Authentication")
        self.root.wait_window(password_dialog.root)
        
        if not password_dialog.password:
            return
            
        input_hash = hashlib.sha256(password_dialog.password.encode()).hexdigest()
        if input_hash != ADMIN_PASSWORD:
            self.voice.speak("Invalid admin password")
            return
        
        # Registrasi wajah baru
        top, right, bottom, left = face_location
        face_img = frame[top:bottom, left:right]
        
        registration_form = RegistrationForm(self.root, face_img, face_encoding)
        self.root.wait_window(registration_form.root)
        
        if registration_form.registration_complete:
            self.attendance_system.load_known_faces()

if __name__ == "__main__":
    app = FaceAttendanceApp()
    app.run()