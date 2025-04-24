import cv2
import sqlite3
import pathlib
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime, date
from PIL import Image, ImageTk
import numpy as np
import face_recognition
from openpyxl import Workbook, load_workbook
import pyttsx3
import pandas as pd

# === SETUP PATHS ===
current_dir = pathlib.Path(__file__).parent
img_dir = current_dir.joinpath('img')
known_faces_dir = current_dir.joinpath('known_faces')
screenshots_dir = current_dir.joinpath('screenshots')
morning_screenshots_dir = screenshots_dir.joinpath('morning')
afternoon_screenshots_dir = screenshots_dir.joinpath('afternoon')
db_path = current_dir.joinpath('faces.db')
spreadsheet_path = current_dir.joinpath('face_data.xlsx')
daily_data_dir = current_dir.joinpath('data_harian')

# === BUAT FOLDER JIKA BELUM ADA ===
for dir_path in [img_dir, known_faces_dir, screenshots_dir, morning_screenshots_dir, 
                afternoon_screenshots_dir, daily_data_dir]:
    os.makedirs(dir_path, exist_ok=True)

# === BUAT / BUKA SPREADSHEET ===
if spreadsheet_path.exists():
    workbook = load_workbook(spreadsheet_path)
else:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Face Data"
    sheet.append(["Name", "Class", "Role", "Image Path", "Log", "Arrival Time", "Return Time", "Duration"])
    workbook.save(spreadsheet_path)

# === KONEKSI DB ===
def init_databases():
    # Main database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS faces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        class_name TEXT,
        role TEXT,
        image_path TEXT,
        encoding BLOB,
        log TEXT,
        timestamp TEXT
    )
    ''')
    conn.commit()
    conn.close()
    
    # Daily log database
    conn = sqlite3.connect('face_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS faces
                 (name TEXT, class_name TEXT, role TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

init_databases()

# === TTS SETUP ===
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# === VARIABEL BANTUAN ===
recognized_faces = set()
register_mode = False
save_screenshot_flag = True

# === FUNGSI UTAMA ===
def save_to_spreadsheet(name, class_name, role, img_path, log, arrival_time, return_time, duration):
    workbook = load_workbook(spreadsheet_path)
    sheet = workbook.active
    sheet.append([name, class_name, role, img_path, log, arrival_time, return_time, duration])
    workbook.save(spreadsheet_path)

def save_to_daily_excel():
    conn = sqlite3.connect('face_data.db')
    df = pd.read_sql_query("SELECT * FROM faces", conn)
    date_str = datetime.now().strftime('%Y-%m-%d')
    file_path = daily_data_dir.joinpath(f'{date_str}.xlsx')
    df.to_excel(file_path, index=False)
    conn.close()

def load_known_faces():
    known_encodings = []
    known_names = []
    known_classes = []
    known_roles = []
    
    # Load from known_faces folder
    for file in os.listdir(known_faces_dir):
        if file.endswith('.jpg') or file.endswith('.png'):
            img_path = os.path.join(known_faces_dir, file)
            image = face_recognition.load_image_file(img_path)
            encoding = face_recognition.face_encodings(image)
            if encoding:
                known_encodings.append(encoding[0])
                known_names.append(os.path.splitext(file)[0])
                
                # Try to get class and role from database
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT class_name, role FROM faces WHERE name = ?", (os.path.splitext(file)[0],))
                result = cursor.fetchone()
                if result:
                    known_classes.append(result[0])
                    known_roles.append(result[1])
                else:
                    known_classes.append("")
                    known_roles.append("")
                conn.close()
    
    # Also load from database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, class_name, role, encoding FROM faces")
    rows = cursor.fetchall()
    for row in rows:
        name, class_name, role, encoding_blob = row
        if name not in known_names:
            known_encodings.append(np.frombuffer(encoding_blob, dtype=np.float64))
            known_names.append(name)
            known_classes.append(class_name)
            known_roles.append(role)
    conn.close()
    
    return known_encodings, known_names, known_classes, known_roles

def recognize_face(face_encoding, known_encodings, known_names, known_classes, known_roles):
    matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.4)
    face_distances = face_recognition.face_distance(known_encodings, face_encoding)
    best_match_index = np.argmin(face_distances) if face_distances.size > 0 else None
    
    if best_match_index is not None and matches[best_match_index]:
        return {
            'name': known_names[best_match_index],
            'class': known_classes[best_match_index],
            'role': known_roles[best_match_index]
        }
    return None

def save_identity(name, class_name, role, face, face_encoding):
    timestamp = datetime.now().timestamp()
    
    # Save to known_faces folder
    img_path = known_faces_dir.joinpath(f'{name}.jpg')
    cv2.imwrite(str(img_path), face)
    
    # Save to img folder with timestamp
    timestamp_img_path = img_dir.joinpath(f'{int(timestamp)}.jpg')
    cv2.imwrite(str(timestamp_img_path), face)
    
    # Save to database
    encoding_blob = face_encoding.tobytes()
    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO faces (name, class_name, role, image_path, encoding, log, timestamp) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (name, class_name, role, str(timestamp_img_path), encoding_blob, '[]', timestamp_str))
    conn.commit()
    
    # Also save to daily log database
    conn = sqlite3.connect('face_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO faces VALUES (?, ?, ?, ?)", (name, class_name, role, timestamp_str))
    conn.commit()
    conn.close()
    
    save_to_spreadsheet(name, class_name, role, str(timestamp_img_path), '[]', '', '', '')

def register_new_face(frame, face, face_encoding):
    global register_mode
    register_mode = True

    def save():
        name = name_entry.get()
        class_name = class_entry.get()
        role = role_entry.get()
        if name and class_name and role:
            save_identity(name, class_name, role, face, face_encoding)
            root.destroy()
            global register_mode
            register_mode = False
            speak(f"Selamat datang, {name}")
        else:
            messagebox.showwarning("Input Error", "Name, Class and Role are required")

    root = tk.Tk()
    root.title("Daftarkan Wajah")
    tk.Label(root, text='Masukkan nama:').pack()
    name_entry = tk.Entry(root)
    name_entry.pack()
    tk.Label(root, text='Masukkan kelas:').pack()
    class_entry = tk.Entry(root)
    class_entry.pack()
    tk.Label(root, text='Masukkan role:').pack()
    role_entry = tk.Entry(root)
    role_entry.pack()
    face_img = Image.fromarray(cv2.cvtColor(face, cv2.COLOR_BGR2RGB))
    face_img = ImageTk.PhotoImage(image=face_img)
    tk.Label(root, image=face_img).pack()
    tk.Button(root, text='Simpan', command=save).pack()
    root.mainloop()

def log_attendance(name, role):
    today = date.today().isoformat()
    now = datetime.now().isoformat()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get or create log entry
    cursor.execute("SELECT id, log FROM faces WHERE name = ?", (name,))
    result = cursor.fetchone()
    
    if result:
        entry_id, log_str = result
        log = eval(log_str) if log_str else []
        
        if len(log) == 0 or log[-1]['date'] != today:
            log.append({'date': today, 'arrival_time': now, 'return_time': None})
            
            # Greeting based on time
            hour = datetime.now().hour
            greeting = "Selamat pagi" if hour < 12 else "Selamat siang" if hour < 17 else "Selamat sore"
            speak(f"{greeting}, {name}")
        else:
            log[-1]['return_time'] = now
            arrival_time = datetime.fromisoformat(log[-1]['arrival_time'])
            return_time = datetime.fromisoformat(log[-1]['return_time'])
            duration = return_time - arrival_time
            duration_str = str(duration)
            
            save_to_spreadsheet(name, "", role, "", str(log), log[-1]['arrival_time'], 
                              log[-1]['return_time'], duration_str)
            speak(f"Selamat jalan, {name}, hati-hati di jalan.")
        
        cursor.execute("UPDATE faces SET log = ? WHERE id = ?", (str(log), entry_id))
        conn.commit()
    
    conn.close()

def get_screenshot_folder():
    now = datetime.now().time()
    morning_start = datetime.strptime('07:30:00', '%H:%M:%S').time()
    morning_end = datetime.strptime('12:00:00', '%H:%M:%S').time()
    afternoon_start = datetime.strptime('14:00:00', '%H:%M:%S').time()
    if morning_start <= now < morning_end:
        return morning_screenshots_dir
    elif afternoon_start <= now:
        return afternoon_screenshots_dir
    else:
        return screenshots_dir

# === MULAI KAMERA ===
def main():
    known_encodings, known_names, known_classes, known_roles = load_known_faces()
    captured_faces = set()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Kamera gagal dibuka.")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Gagal membaca frame.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            face_image = frame[top:bottom, left:right]
            result = recognize_face(face_encoding, known_encodings, known_names, known_classes, known_roles)
            
            if result:
                name = result['name']
                role = result['role']
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(frame, role, (left, top - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

                if name not in captured_faces:
                    captured_faces.add(name)
                    log_attendance(name, role)
                    
                    # Save screenshot
                    folder = get_screenshot_folder()
                    img_name = folder.joinpath(f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
                    cv2.imwrite(str(img_name), face_image)
            else:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, "Unknown", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                if not register_mode:
                    cv2.putText(frame, "Tekan 's' untuk daftar", (left, bottom + 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        cv2.imshow("Face Recognition", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            save_to_daily_excel()
            break
        elif key == ord('s') and not register_mode:
            if len(face_locations) > 0:
                (top, right, bottom, left) = face_locations[0]
                face = frame[top:bottom, left:right]
                face_encoding = face_encodings[0]
                register_new_face(frame, face, face_encoding)
                # Reload known faces after registration
                known_encodings, known_names, known_classes, known_roles = load_known_faces()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()