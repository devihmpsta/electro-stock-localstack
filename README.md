# ElectroStock

Proyek fondasi sistem manajemen stok dan inventaris modern menggunakan **Flask** dengan arsitektur bersih (**Clean Architecture**).

## Daftar Isi
- [Arsitektur Proyek](#arsitektur-proyek)
- [Teknologi yang Digunakan](#teknologi-yang-digunakan)
- [Persyaratan Sistem](#persyaratan-sistem)
- [Struktur Direktori](#struktur-direktori)
- [Cara Instalasi & Menjalankan Aplikasi](#cara-instalasi--menjalankan-aplikasi)
  - [Menggunakan Virtual Environment (Lokal)](#menggunakan-virtual-environment-lokal)
  - [Menggunakan Docker](#menggunakan-docker)
- [Variabel Lingkungan (.env)](#variabel-lingkungan-env)

---

## Arsitektur Proyek
Proyek ini mengimplementasikan konsep Clean Architecture dengan pembagian layer yang jelas sebagai berikut:

*   **Domain Layer (`app/domain`)**: Layer terdalam yang berisi logika bisnis inti dan entitas (model). Layer ini murni berisi objek Python (dataclass) tanpa ketergantungan pada framework web atau database.
*   **Application Layer (`app/application`)**: Layer yang menampung use case dan layanan (services). Mengatur alur data dan koordinasi logika bisnis.
*   **Infrastructure Layer (`app/infrastructure`)**: Layer terluar yang berisi detail teknis seperti rute HTTP (Flask Blueprints), template HTML (Jinja2), file statis (CSS/JS), dan integrasi database (di masa mendatang).
*   **App Factory (`app/__init__.py`)**: Desain pola untuk inisialisasi aplikasi Flask yang bersih dan modular.
*   **Config (`app/config.py`)**: Konfigurasi terpusat berbasis environment (Development, Production, Testing).

---

## Struktur Direktori
```text
electro-stock/
├── app/
│   ├── __init__.py                # App Factory (create_app)
│   ├── config.py                  # Konfigurasi Konteks (Dev, Prod, Test)
│   ├── domain/                    # Layer Domain (Core Entitas)
│   │   ├── __init__.py
│   │   └── models/
│   │       └── __init__.py        # Entitas Domain (StockItem)
│   ├── application/               # Layer Aplikasi (Business Logic)
│   │   ├── __init__.py
│   │   └── services/
│   │       └── __init__.py        # Business Service (StockService)
│   ├── infrastructure/            # Layer Infrastruktur (Web, Assets)
│   │   ├── __init__.py
│   │   ├── routes/                # Flask Blueprints
│   │   │   ├── __init__.py
│   │   │   └── main.py            # Rute Utama "/"
│   │   ├── templates/             # Jinja2 HTML Templates
│   │   │   ├── base.html
│   │   │   └── index.html
│   │   └── static/                # Static Assets (CSS, JS)
│   │       ├── css/
│   │       │   └── style.css
│   │       └── js/
│   │           └── main.js
│   └── utils/                     # Cross-cutting Utilities
│       └── __init__.py
├── .env                           # File env lokal (terabaikan di git)
├── .env.example                   # Contoh konfigurasi environment
├── .gitignore                     # Git ignore rules
├── Dockerfile                     # Image Builder Python 3.12
├── docker-compose.yml             # Local Development Orchestrator
├── requirements.txt               # Daftar Dependensi Python
└── README.md                      # Dokumentasi Proyek
```

---

## Teknologi yang Digunakan
*   **Python 3.12+**
*   **Flask 3.0.3** - Web Framework
*   **Gunicorn 22.0.0** - WSGI Server untuk produksi
*   **Docker & Docker Compose** - Containerization & Orchestration

---

## Persyaratan Sistem
*   Python 3.12 atau versi lebih baru terinstal.
*   Docker & Docker Compose terinstal (untuk menjalankan via container).

---

## Cara Instalasi & Menjalankan Aplikasi

### Menggunakan Virtual Environment (Lokal)

1. **Buka terminal dan masuk ke direktori proyek:**
   ```bash
   cd electro-stock
   ```

2. **Buat virtual environment Python:**
   ```bash
   python -m venv .venv
   ```

3. **Aktifkan virtual environment:**
   *   **Windows (PowerShell):**
       ```powershell
       .venv\Scripts\Activate.ps1
       ```
   *   **Linux/macOS:**
       ```bash
       source .venv/bin/activate
       ```

4. **Instal dependensi proyek:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Salin file konfigurasi env:**
   ```bash
   copy .env.example .env
   ```
   *(Untuk Linux/macOS gunakan `cp .env.example .env`)*

6. **Jalankan aplikasi:**
   ```bash
   flask run
   ```
   Aplikasi akan berjalan di `http://127.0.0.1:5000`.

---

### Menggunakan Docker

1. **Bangun dan jalankan container di latar belakang (background):**
   ```bash
   docker-compose up -d --build
   ```
   *(Flag `-d` digunakan agar kontainer berjalan di latar belakang dan terminal Anda tetap bebas dari tumpukan log).*

2. **Akses aplikasi di browser:**
   Buka peramban Anda dan arahkan ke [http://localhost:5000](http://localhost:5000).

3. **Matikan container:**
   ```bash
   docker-compose down
   ```

---

### Kredensial Login Default

Untuk masuk ke halaman dashboard, gunakan akun admin bawaan berikut (otomatis dibuat pada saat migrasi/seeding database pertama kali):

*   **Username:** `admin`
*   **Password:** `admin123`

---

### Manajemen Database (pgAdmin 4)

Untuk mempermudah pengelolaan database PostgreSQL, Anda dapat menggunakan **pgAdmin 4** yang berjalan di dalam container Docker.

#### 1. Menjalankan Docker Compose
Pastikan container berjalan dengan perintah:
```bash
docker-compose up -d
```
Service `electrostock-pgadmin` akan aktif secara otomatis pada port `5050`.

#### 2. Membuka pgAdmin
Buka browser Anda dan akses:
[http://localhost:5050](http://localhost:5050)

#### 3. Login ke pgAdmin
Gunakan kredensial default yang telah diatur di berkas `.env` (atau bawaan):
*   **Email:** `admin@electrostock.com` (sesuai `PGADMIN_DEFAULT_EMAIL` di `.env`)
*   **Password:** `adminpass` (sesuai `PGADMIN_DEFAULT_PASSWORD` di `.env`) 

#### 4. Menambahkan Koneksi ke PostgreSQL
Setelah login berhasil, ikuti langkah berikut untuk menyambungkan pgAdmin ke PostgreSQL:
1.  Klik kanan pada **Servers** di sidebar kiri -> pilih **Register** -> **Server...**.
2.  Pada tab **General**:
    *   **Name:** Isi nama bebas, contoh: `ElectroStock DB`.
3.  Pada tab **Connection**:
    *   **Host name/address:** Isi `postgres` (ini adalah nama service database di Docker Network).
    *   **Port:** `5432` (port default PostgreSQL).
    *   **Maintenance database:** `electrostock` (sesuai `DATABASE_NAME` di `.env`).
    *   **Username:** `electrostock_user` (sesuai `DATABASE_USER` di `.env`).
    *   **Password:** `electrostock_pass` (sesuai `DATABASE_PASSWORD` di `.env`).
    *   Centang **Save password?** agar tidak perlu mengetik ulang kata sandi.
4.  Klik **Save**.

#### 5. Membuka Database ElectroStock
Di sidebar kiri pgAdmin, navigasikan ke:
`Servers` -> `ElectroStock DB` -> `Databases` -> `electrostock` -> `Schemas` -> `public` -> `Tables`.

#### 6. Melihat Tabel Aplikasi
Di bawah menu `Tables`, Anda akan menemukan tabel-tabel utama ElectroStock:
*   `users` (Data pengguna/admin)
*   `kategori` (Data kategori barang)
*   `barang` (Data barang dan stok)
*   `stock_history` (Riwayat transaksi stok masuk/keluar)

#### 7. Menjalankan SQL Query
Untuk menjalankan perintah SQL kustom:
1.  Klik kanan pada database `electrostock` atau tabel apa saja.
2.  Pilih **Query Tool**.
3.  Tuliskan SQL query Anda (misal: `SELECT * FROM barang;`).
4.  Tekan tombol **F5** atau klik tombol **Play (Execute)** untuk melihat hasilnya.

#### 8. Mengedit Data secara Langsung (Direct Data Editing)
Anda juga dapat mengedit data langsung dari antarmuka visual pgAdmin:
1.  Klik kanan pada tabel yang ingin diedit (misal: `barang`).
2.  Pilih **View/Edit Data** -> **All Rows**.
3.  Klik dua kali pada sel yang ingin diubah datanya.
4.  Klik tombol **Save Data Changes (F6)** di panel atas untuk menyimpan perubahan secara langsung ke database.

---

### Monitoring & Troubleshooting

Seluruh container dan resource AWS Mock pada LocalStack dapat dipantau secara langsung melalui **Stackport**.

#### 1. Cara Mengakses Stackport (Dashboard Monitoring)
Buka peramban Anda dan arahkan ke [http://localhost:8080](http://localhost:8080).
Melalui antarmuka Stackport, Anda dapat:
*   Melihat daftar bucket S3 (`electrostock-bucket`).
*   Memantau status dan detail instance EC2 yang sedang berjalan.

#### 2. Cara Melihat Container (Docker)
Untuk melihat semua container yang aktif beserta status kesehatannya (*healthcheck*):
```bash
docker ps
```
Atau untuk melihat semua container (termasuk yang tidak aktif):
```bash
docker ps -a
```

#### 3. Cara Melihat Volume (Docker)
Untuk melihat semua volume data yang digunakan oleh PostgreSQL dan LocalStack:
```bash
docker volume ls
```
Untuk menginspeksi konfigurasi detail dari volume tertentu:
```bash
docker volume inspect <nama_volume>
```

#### 4. Cara Melihat Log Aplikasi (Docker Logs)
Untuk memantau log *runtime* dan transaksi server Flask (`web`) secara langsung (*real-time*):
```bash
docker logs -f electro-stock-web
```
Untuk memeriksa log database PostgreSQL atau LocalStack:
```bash
docker logs -f electro-stock-postgres
docker logs -f electro-stock-localstack
```

#### 5. Cara Memeriksa LocalStack secara Manual
Selain melalui Stackport, Anda dapat melakukan verifikasi langsung ke *endpoint* LocalStack:
*   **Memeriksa Bucket S3:**
    ```bash
    curl http://localhost:4566/electrostock-bucket
    ```
*   **Memeriksa List EC2 Instance via AWS CLI:**
    *(Jika AWS CLI terpasang pada mesin host)*
    ```bash
    aws --endpoint-url=http://localhost:4566 ec2 describe-instances
    ```

