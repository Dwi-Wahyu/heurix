Skema saat ini sudah berhasil menyimpan dan menggunakan riwayat percakapan untuk mendukung ingatan AI
dan fitur persona shift.

Berikut adalah analisis teknis bagaimana sistem "mengingat" dan melakukan "shift":

1.  Penyimpanan Permanen: Setiap giliran (pertanyaan AI dan jawaban Anda) disimpan secara permanen di
    database dalam tabel SessionTurn. Ini memastikan bahwa meskipun koneksi terputus, riwayat tetap ada.
2.  Konteks yang Utuh: Setiap kali AI akan merespon, fungsi build_chat_history di brain.py akan mengambil
    data dari database tersebut dan menyusunnya kembali menjadi format percakapan (Assistant vs User).
    Seluruh riwayat ini dikirimkan kembali ke AI Groq, sehingga AI tahu apa yang sudah ditanyakan
    sebelumnya dan apa jawaban Anda.
3.  Logika Persona Shift:
    - AI memberikan skor (answer_quality_score) untuk setiap jawaban Anda.
    - Fungsi should_shift_persona memantau skor ini. Jika skor Anda di bawah ambang batas (misalnya,
      terlalu banyak kata pengisi atau jawaban tidak nyambung), sistem akan mengubah
      session.currentPersona.
    - Pada giliran berikutnya, AI akan menerima instruksi sistem yang berbeda (misalnya, dari Formal
      menjadi Intimidating) berdasarkan perubahan tersebut.

Perbaikan yang baru saja saya lakukan:
Saya menemukan dan memperbaiki masalah kecil di mana jawaban terakhir user sempat terkirim dua kali
(duplikasi) dalam konteks history ke AI. Sekarang, pengiriman history sudah lebih bersih:

- past_turns: Berisi semua percakapan lama yang sudah selesai.
- current_question: Pertanyaan yang sedang Anda jawab saat ini.
- new_answer_transcript: Jawaban terbaru yang baru saja Anda ucapkan.

Dengan skema ini, AI akan memiliki "ingatan" yang sangat akurat dan dapat melakukan transisi persona
secara halus berdasarkan performa wawancara Anda
