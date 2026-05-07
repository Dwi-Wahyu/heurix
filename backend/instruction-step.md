Perintah yang Harus Dijalankan:

Pastikan Anda berada di direktori utama proyek, lalu jalankan perintah berikut:

1.  Membangun dan menjalankan seluruh layanan:

1 docker compose up --build -d

2.  Melihat log untuk memastikan tidak ada error:

1 docker compose logs -f

3.  Melakukan migrasi database (jika diperlukan):

1 # Masuk ke container frontend untuk menjalankan drizzle-kit
2 docker exec -it hiready_frontend bun run db:push
