Sesuai dengan analisis terhadap masalah pada @src/routes/session/interview/+page.svelte dan perbandingan
dengan @PRD.md serta file instruksi model, saya telah melakukan perbaikan berikut:

1.  Memperbaiki Visibilitas Model (Masalah Skala):
    - Menghapus model.scale.setScalar(0.01) yang sebelumnya mengecilkan model menjadi hanya ~1.8cm (jika
      dalam meter), sehingga kamera melewati model tersebut. Model GLTF standar biasanya dalam satuan
      meter, sehingga skala default 1.0 adalah yang benar.
2.  Kamera Fokus "Neck-Up" (Leher ke Kepala):
    - Memperbarui algoritma Dynamic Camera Focus. Sekarang kamera secara otomatis menghitung area 18%
      teratas dari tinggi model (area leher ke atas) dan memposisikan kamera agar area tersebut mengisi
      ~85% tinggi layar.
    - Mengatur near plane ke 0.01 agar model tidak terpotong saat kamera berada sangat dekat dengan
      wajah.
3.  Pencahayaan & Rendering:
    - Menggunakan ACESFilmicToneMapping untuk kualitas visual yang lebih sinematik dan modern.
    - Menambahkan keyLight.target ke dalam scene agar pencahayaan benar-benar menyorot ke arah wajah
      model secara akurat.
4.  Animasi Viseme:
    - Memastikan sistem lip-sync menggunakan teknik amplitudo suara yang sinkron dengan gerakan mulut
      model melalui FaceAnimator. Gerakan mulut kini diatur untuk membuka secara natural mengikuti
      intonasi suara dari backend.

Sekarang, model AI seharusnya muncul dengan tampilan close-up (dari leher ke atas kepala) dan bergerak
secara interaktif saat berbicara, sesuai dengan instruksi pada PRD.
