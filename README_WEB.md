# FASIH-SM Web Automation - User Guide

Aplikasi web automation untuk fasih-sm.bps.go.id, menggantikan script Python CLI dengan antarmuka web yang modern.

## 🚀 Cara Menjalankan Aplikasi

Anda perlu menjalankan **Backend** dan **Frontend** secara bersamaan di dua terminal berbeda.

### 1. Menjalankan Backend (Server)

Buka terminal baru, lalu jalankan perintah berikut:

```powershell
# Masuk ke folder backend
cd d:\2026\SCRAPING\FASIH-SM\backend

# Install dependencies (hanya pertama kali)
pip install -r requirements.txt

# Jalankan server
python app.py
```

Server akan berjalan di `http://localhost:5000`.

### 2. Menjalankan Frontend (Tampilan Web)

Buka terminal **kedua**, lalu jalankan:

```powershell
# Masuk ke folder frontend
cd d:\2026\SCRAPING\FASIH-SM\frontend

# Install dependencies (hanya pertama kali, sudah dilakukan oleh AI)
# npm install

# Jalankan mode development
npm run dev
```

Aplikasi akan berjalan di `http://localhost:5173` (atau port lain yang ditampilkan). Buka alamat tersebut di browser (Chrome/Edge).

---

## 📖 Cara Penggunaan

### 1. Login
- Masukkan username dan password SSO BPS/LDAP Anda.
- Browser Chrome otomatis akan terbuka (jangan ditutup).
- Jika ada OTP, masukkan kode OTP di halaman web (Web UI).
- Setelah login berhasil, browser akan **minimize** otomatis.

### 2. Dashboard
- Pilih **Daftar Survei**.
- Pilih **Periode Survei**.
- Pilih **Wilayah** (Provinsi -> Kabupaten).
- Panel aksi akan aktif jika semua pilihan sudah lengkap.

### 3. Fitur / Aksi
Semua proses berjalan di background, Anda bisa melihat log secara real-time.

- **Download Raw Data**: Mengunduh data isian (answers) ke Excel.
- **Approve All**: Melakukan approval untuk semua assignment yang memenuhi syarat.
- **Revoke**: Membatalkan approval (jika status completed).
- **Reject**: Menolak assignment (jika status submitted).

### 4. Download Hasil
Setelah proses selesai, tombol **Download Result** akan muncul di panel log. Klik untuk mengunduh file Excel hasil proses/log.

### 5. Logout
Klik tombol "Sign Out" di pojok kanan atas untuk keluar dan menutup browser automation.

---

## ⚠️ Catatan Penting
- **Jangan menutup paksa** jendela browser Chrome yang terbuka otomatis. Biarkan aplikasi yang mengaturnya (minimize/close).
- File hasil download disimpan otomatis juga di folder `backend/output`.
