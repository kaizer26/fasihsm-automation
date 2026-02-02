# FASIH-SM Automation Tool 🚀

FASIH-SM adalah alat otomatisasi berbasis web untuk mempermudah pengelolaan survei dan pengunduhan data mentah dari platform FASIH-SM BPS. Alat ini mengintegrasikan Selenium untuk otomatisasi browser dan Flask/React untuk antarmuka pengguna yang modern.

## ✨ Fitur Utama
- **One-Click Login (Session Persistence)**: Mengingat sesi login Anda sehingga tidak perlu input OTP berulang kali.
- **Smart Column Selection**: Pilih hanya variabel yang Anda butuhkan sebelum mendownload data mentah.
- **Smart Column Sorting**: Mengurutkan kolom Excel secara cerdas berdasarkan urutan kuesioner (Blok > Rincian > Sub-rincian).
- **History Download**: Akses cepat ke riwayat unduhan sebelumnya tanpa harus memproses ulang.
- **Support Jaringan Lokal (LAN)**: Bisa diakses oleh rekan kerja dalam satu jaringan WiFi.
- **UI Modern & Dark Mode**: Antarmuka responsif menggunakan Bootstrap 5.

## � Panduan Instalasi

Jika PC Anda belum memiliki prasyarat di atas, ikuti langkah berikut:

### 1. Install Python
1. Unduh installer Python 3.10+ di [python.org/downloads](https://www.python.org/downloads/windows/).
2. Jalankan installer.
3. **PENTING**: Centang kotak **"Add Python to PATH"** di bagian bawah sebelum klik **Install Now**.
4. Verifikasi dengan membuka Command Prompt/PowerShell dan ketik: `python --version`.

### 2. Install Node.js
1. Unduh installer Node.js versi LTS di [nodejs.org](https://nodejs.org/).
2. Jalankan installer dan ikuti petunjuk (klik Next sampai selesai).
3. Verifikasi dengan membuka Command Prompt/PowerShell dan ketik: `node -v` dan `npm -v`.

---

## 🚀 Cara Menjalankan
Cukup ikuti langkah mudah ini:

1. **Clone Repository**
   ```bash
   git clone https://github.com/kaizer26/fasihsm-automation.git
   cd fasihsm-automation
   ```

2. **Jalankan Setup & Start**
   Double-click file `RUN-ME.bat`. File ini akan otomatis:
   - Membuat Virtual Environment Python.
   - Menginstall semua library backend (Flask, Selenium, Pandas, dll).
   - Menginstall semua library frontend (React, Bootstrap).
   - Menjalankan server backend dan frontend sekaligus.

3. **Buka Browser**
   Buka `http://localhost:5173` di browser Anda.

## 🔄 Cara Update ke GitHub
Jika Anda mengganti kode dan ingin meng-update repository di GitHub:
1. Double-click `update-repo.bat`.
2. Masukkan pesan perubahannya.
3. Tunggu sampai selesai.

## 🖥️ Akses via Jaringan (Server Mode)
Jika ingin membagikan akses ke rekan kerja di jaringan WiFi yang sama:
1. Klik kanan `setup-firewall.bat` -> **Run as Administrator** (hanya perlu sekali).
2. Jalankan `RUN-ME.bat`.
3. Bagikan IP Address yang muncul di jendela terminal ke rekan Anda (contoh: `http://192.168.1.100:5173`).

## 📁 Struktur Folder
- `backend/`: Server Flask, Selenium Manager, dan API integration.
- `frontend/`: Aplikasi React.js dengan Bootstrap 5.
- `output/`: Folder penyimpanan otomatis untuk session, cache wilayah, dan hasil download.

---
**Catatan Penting**: Browser Chrome akan terbuka secara otomatis saat pertama kali login untuk menangani SSO BPS. Jangan tutup browser tersebut sampai proses login selesai.
