# Reduksi Noise Audio  

Proyek mini ini adalah aplikasi desktop sederhana yang dibuat dengan **Python** untuk mendemonstrasikan proses reduksi noise (gangguan suara) pada sinyal audio menggunakan **filter low-pass**.

---

## Anggota Kelompok  
- Mohammad Ridho Cahyono  

---

## Deskripsi Proyek  
Aplikasi **Reduksi Noise Audio** ini dirancang untuk memuat file audio `.wav` dari pengguna, kemudian secara otomatis menambahkan **noise Gaussian** ke dalamnya.  

Setelah itu, aplikasi menerapkan **filter low-pass Butterworth** untuk mengurangi noise tersebut.  

Fitur utama aplikasi:  
- Memutar **audio asli**, **audio bernoise**, dan **audio terfilter** untuk perbandingan.  
- Menyediakan **visualisasi sinyal audio** dalam domain waktu dan frekuensi (spektrum).  
- Memberikan gambaran grafis efek noise dan proses pemfilteran.  

---

## Link YouTube Presentasi  
*[Pengolahan Sinyal Digital - Noise dan Filtering - Kelompok 3](https://youtu.be/-C1X8heG3kE)*  

---

## Cara Menjalankan Proyek  

Ikuti langkah-langkah di bawah ini untuk mengunduh dan menjalankan proyek dari GitHub.  

### 1. Prasyarat  
Pastikan Anda telah menginstal **Python 3.x** di sistem Anda.  

### 2. Unduh Proyek dari GitHub  

**a. Menggunakan Git (Direkomendasikan):**

    git clone https://github.com/mohammadridhocahyono/Reduksi-Noise-Audio.git
    cd Reduksi-Noise-Audio

b. Unduh ZIP Manual:

Kunjungi halaman repositori GitHub proyek Anda.

Klik tombol "Code" → "Download ZIP".

Ekstrak file ZIP ke lokasi yang Anda inginkan.

3. Instal Dependensi

Jalankan perintah berikut di direktori proyek:

    pip install -r requirements.txt

4. Jalankan Aplikasi

Jalankan aplikasi utama dengan perintah:

    python mini-project.py

Maka akan muncul jendela aplikasi "Mini Proyek: Reduksi Noise Audio".

5. Menggunakan Aplikasi

Muat Audio.wav: Klik tombol "Muat Audio.wav" untuk memilih file audio.

Dengarkan Audio: Gunakan tombol:

► Putar Audio Asli

► Putar Audio Noise

► Putar Audio Filter

Lihat Visualisasi: Amati grafik sinyal audio dalam domain waktu & frekuensi.