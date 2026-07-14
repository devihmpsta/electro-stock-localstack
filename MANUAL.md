# Panduan Penggunaan & Setup ElectroStock

ElectroStock adalah sistem manajemen stok dan inventaris modern berbasis **Flask** yang berjalan di atas kontainer **Docker**. Panduan ini akan memandu Anda melakukan setup awal pada komputer server (host) dan cara mengakses aplikasi menggunakan peramban (browser) di perangkat lain (smartphone, tablet, atau laptop lain) yang berada dalam satu jaringan lokal.

---

## Daftar Isi
1. [Arsitektur & Port Layanan](#1-arsitektur--port-layanan)
2. [Persyaratan Sistem & Jaringan](#2-persyaratan-sistem--jaringan)
3. [Setup Awal di Komputer Server/Host](#3-setup-awal-di-komputer-serverhost)
4. [Konfigurasi Firewall (Penting untuk Akses Perangkat Lain)](#4-konfigurasi-firewall-penting-untuk-akses-perangkat-lain)
5. [Akses Aplikasi dari Perangkat Lain (Client)](#5-akses-aplikasi-dari-perangkat-lain-client)
6. [Panduan Fitur Aplikasi](#6-panduan-fitur-aplikasi)
7. [Pemecahan Masalah (Troubleshooting)](#7-pemecahan-masalah-troubleshooting)

---

## 1. Arsitektur & Port Layanan

Aplikasi ini menggunakan beberapa layanan terintegrasi dalam Docker Compose:
*   **Web App (Flask)**: Layanan utama aplikasi pada port `5000`.
*   **PostgreSQL**: Database relasional pada port `5432`.
*   **LocalStack**: Emulator AWS (S3 & EC2) pada port `4566`.
*   **Stackport**: Antarmuka web (UI) untuk melihat isi emulator AWS/LocalStack pada port `8080`.
*   **pgAdmin**: Antarmuka web (UI) manajemen database PostgreSQL pada port `5050`.

---

## 2. Persyaratan Sistem & Jaringan

Sebelum memulai, pastikan kondisi berikut terpenuhi:
1.  **Perangkat Utama (Server/Host)**: Komputer yang menjalankan Docker Desktop dan menyimpan source code aplikasi.
2.  **Perangkat Klien (Client)**: HP, tablet, atau laptop lain yang memiliki web browser.
3.  **Koneksi Jaringan**: Kedua perangkat (Server & Client) **harus terhubung ke jaringan Wi-Fi atau LAN yang sama**.
4.  **Docker & Docker Compose**: Sudah terinstal di Komputer Server.

---

## 3. Setup Awal di Komputer Server/Host

Ikuti langkah berikut untuk menyalakan aplikasi di komputer server Anda:

### Langkah 1: Siapkan File Konfigurasi Environment (`.env`)
Pastikan file `.env` sudah ada di direktori utama proyek (`electro-stock/`). Jika belum ada:
1.  Salin file `.env.example` menjadi `.env`.
2.  Buka `.env` dan atur email & password untuk pgAdmin, contoh:
    ```env
    PGADMIN_DEFAULT_EMAIL=admin@electrostock.local
    PGADMIN_DEFAULT_PASSWORD=admin123
    ```

### Langkah 2: Jalankan Container Docker
1.  Buka Terminal (PowerShell di Windows atau Terminal di macOS/Linux).
2.  Masuk ke folder proyek `electro-stock`:
    ```bash
    cd electro-stock
    ```
3.  Jalankan perintah berikut untuk membangun dan menghidupkan seluruh kontainer:
    ```bash
    docker-compose up -d --build
    ```
    *Flag `-d` memastikan kontainer berjalan di latar belakang (background mode).*

### Langkah 3: Verifikasi Status Kontainer
Pastikan semua kontainer berjalan lancar (berstatus *Up* atau *Healthy*):
```bash
docker-compose ps
```
Semua kontainer (`electro-stock-web`, `electro-stock-postgres`, `electro-stock-localstack`, `electro-stock-stackport`, dan `electrostock-pgadmin`) harus berstatus berjalan.

---

## 4. Konfigurasi Firewall (Penting untuk Akses Perangkat Lain)

Secara default, sistem operasi (terutama Windows) memblokir koneksi masuk dari jaringan luar ke port komputer Anda demi alasan keamanan. Agar perangkat lain bisa mengakses aplikasi, Anda harus membuka port di firewall.

### Konfigurasi di Windows:
1.  Tekan tombol **Windows**, cari **Windows Defender Firewall with Advanced Security**, lalu buka.
2.  Pada panel kiri, klik **Inbound Rules** (Aturan Masuk).
3.  Pada panel kanan, klik **New Rule...** (Aturan Baru).
4.  Pilih **Port**, lalu klik **Next**.
5.  Pilih **TCP** dan pada bagian **Specific local ports**, masukkan port yang dibutuhkan: `5000, 4566, 8080, 5050` kemudian klik **Next**.
6.  Pilih **Allow the connection** (Izinkan koneksi), lalu klik **Next**.
7.  Centang semua pilihan (**Domain, Private, Public**), lalu klik **Next**.
8.  Beri nama aturan ini (misalnya: `ElectroStock Services`), lalu klik **Finish**.

### Cara Mengetahui IP Address Lokal Server:
Anda membutuhkan IP Address lokal komputer Server agar perangkat lain tahu tujuan koneksi.
*   **Windows**: Buka cmd/PowerShell, ketik `ipconfig`. Cari adaptor jaringan aktif Anda (misalnya *Wireless LAN adapter Wi-Fi*) dan catat nilai **IPv4 Address** (biasanya berupa `192.168.x.x` atau `10.x.x.x`, contoh: `192.168.1.15`).
*   **macOS / Linux**: Buka terminal, ketik `ifconfig` or `ip a`. Cari alamat IP inet lokal Anda.

---

## 5. Akses Aplikasi dari Perangkat Lain (Client)

Setelah server menyala dan port firewall dibuka, ikuti langkah berikut di perangkat klien (misalnya Smartphone Anda):

1.  Pastikan Smartphone terhubung ke **Wi-Fi yang sama** dengan komputer server.
2.  Buka Google Chrome, Safari, atau browser lainnya di HP.
3.  Ketikkan alamat URL berikut di address bar:
    ```text
    http://<IP-ADDRESS-SERVER>:5000
    ```
    *Ganti `<IP-ADDRESS-SERVER>` dengan IP Address lokal server yang Anda dapatkan di bagian 4 (Contoh: `http://192.168.1.15:5000`).*
4.  Laman Login ElectroStock akan muncul di layar HP Anda.

### Informasi Kredensial Akses Default:
*   **Halaman Utama (Aplikasi Inventaris)**
    *   **URL**: `http://<IP-ADDRESS-SERVER>:5000`
    *   **Username**: `admin`
    *   **Password**: `admin123`
*   **Halaman pgAdmin (Manajemen Database)**
    *   **URL**: `http://<IP-ADDRESS-SERVER>:5050`
    *   **Email & Password**: Sesuai yang Anda konfigurasi di file `.env`.
*   **Halaman Stackport (UI S3 Bucket)**
    *   **URL**: `http://<IP-ADDRESS-SERVER>:8080`
    *   *Tanpa login, langsung menampilkan daftar bucket dan file yang diunggah ke S3 LocalStack.*

---

## 6. Panduan Fitur Aplikasi

Sistem ElectroStock terbagi menjadi beberapa modul utama yang responsif dan dapat dioperasikan dengan nyaman lewat perangkat mobile maupun desktop:

### A. Dashboard
*   Menampilkan ringkasan total kategori, jenis barang, sisa stok, dan status sistem secara waktu nyata (real-time).
*   Dilengkapi dengan indikator status sistem (Active/Pulse) dan notifikasi instan jika terdapat barang yang memiliki stok menipis (Low Stock).

### B. Kelola Kategori
*   **Tambah Kategori**: Membuat kategori baru. Sistem secara otomatis mencocokkan kata kunci kategori (misal: "laptop", "gadget", "kabel") untuk memasangkan ikon Lucide yang cantik dan warna aksen secara dinamis.
*   **Daftar Kategori**: Menampilkan jumlah barang terdaftar per kategori dan menyediakan tombol Edit serta Hapus.

### C. Kelola Barang
*   **Tambah/Edit Barang**: Menyediakan form pengisian kode barang, nama, kategori, harga, stok awal, serta **Lokasi Rak** penyimpanan (misal: Rak A-05).
*   **Unggah Foto**: Anda dapat mengunggah gambar barang. Gambar ini secara otomatis disimpan di emulator AWS S3 (LocalStack).
*   **Preview Foto**: Klik pada foto mini (thumbnail) di daftar barang untuk melihat preview foto beresolusi penuh menggunakan efek modal popup yang elegan.
*   **Sesuaikan Stok**: Menu khusus (ikon shuffle) untuk menambah/mengurangi stok dengan cepat disertai pencatatan riwayat (stock history log).
*   **Hapus Barang**: Menghapus data barang beserta berkas fotonya yang tersimpan di S3 secara permanen.

### D. EC2 Monitor
*   Antarmuka monitoring simulasi server cloud AWS EC2 yang terintegrasi dengan LocalStack.
*   Menampilkan daftar instans server aktif, alamat IP publik emulator, tipe instans, dan status *running/stopped*.

### E. Analytics
*   Menyajikan visualisasi grafik interaktif mengenai sebaran stok barang, produk terlaris, dan kapasitas pergudangan untuk mendukung pengambilan keputusan.

---

## 7. Pemecahan Masalah (Troubleshooting)

| Masalah | Penyebab | Solusi |
| :--- | :--- | :--- |
| **Halaman tidak bisa diakses dari HP (Error: Connection Timed Out)** | Perangkat tidak berada di jaringan yang sama ATAU port `5000` terblokir oleh firewall server. | 1. Pastikan kedua perangkat terhubung ke Wi-Fi yang sama.<br>2. Verifikasi aturan masuk (Inbound Rules) port `5000` di Windows Firewall.<br>3. Pastikan Anda mengetik alamat IP yang benar (bukan `localhost` atau `127.0.0.1` di HP). |
| **Foto barang tidak muncul di HP** | Port AWS LocalStack (`4566`) terblokir oleh firewall server. | Buka Windows Firewall dan pastikan port `4566` ditambahkan ke Inbound Rules. Aplikasi telah dikonfigurasi untuk secara otomatis mengalihkan URL gambar dari `localhost:4566` ke IP server secara dinamis ketika diakses dari luar. |
| **Gagal Login (Salah Password)** | Database kosong atau menggunakan data lama. | Hentikan Docker Compose dan hapus volume database untuk mereset data: <br>`docker-compose down -v`<br>Lalu jalankan ulang dengan:<br>`docker-compose up -d --build` |
| **Aplikasi Lambat atau Stuck** | Keterbatasan memori kontainer Docker. | Buka Docker Desktop, masuk ke Settings -> Resources, lalu tingkatkan alokasi CPU dan RAM untuk Docker Engine. |

---

*Catatan: Untuk mematikan seluruh layanan setelah selesai digunakan, jalankan perintah `docker-compose down` dari direktori utama proyek di komputer server. Data di database akan tetap aman karena disimpan di dalam volume Docker lokal (`electrostock-postgres-data`).*
