import { config } from 'dotenv';
config();

import * as schema from '../schema';
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import { createId } from '@paralleldrive/cuid2';

const client = postgres(process.env.DATABASE_URL ?? '');
const db = drizzle(client, { schema });

// ============================================================
// DATA INSTITUSI
// ============================================================

const institutions = [
	// ─── BUMN — KEUANGAN & PERBANKAN ───────────────────────────
	{
		name: 'Bank Mandiri',
		description:
			'Bank BUMN terbesar di Indonesia berdasarkan total aset. Bergerak di bidang perbankan korporat, komersial, ritel, dan digital banking.',
		llmContext: `Bank Mandiri adalah bank terbesar Indonesia dengan budaya TIPCE (Trustworthy, Integrity, Professionalism, Customer Focus, Excellence). Wawancara Bank Mandiri sangat menekankan pada: (1) integritas dan anti-korupsi — kandidat wajib mampu menjelaskan situasi etis dengan tegas; (2) orientasi pada nasabah — setiap jawaban idealnya memperlihatkan empati dan solusi; (3) kemampuan analitis dan kerja di bawah tekanan; (4) adaptabilitas terhadap transformasi digital. Pewawancara biasanya menggunakan metode STAR (Situation, Task, Action, Result) dan menggali pengalaman konkret. Hindari jawaban generik — kandidat yang berhasil selalu membawa data atau contoh nyata.`,
		track: 'corporate' as const,
		defaultAvatarId: 'avatar_professional_man'
	},
	{
		name: 'Bank Rakyat Indonesia (BRI)',
		description:
			'Bank BUMN fokus pada segmen UMKM dan mikro. Jaringan terluas di Indonesia dengan misi memberdayakan ekonomi rakyat.',
		llmContext: `BRI memiliki tagline "Melayani dengan Setulus Hati" dan nilai AKHLAK BUMN. Wawancara BRI sangat berfokus pada: (1) semangat melayani — kandidat harus menunjukkan orientasi pelayanan yang tulus bukan sekadar profesional; (2) pemahaman segmen UMKM dan mikro — pewawancara sering bertanya tentang pengalaman berinteraksi dengan masyarakat kecil; (3) ketahanan di lapangan — posisi AO (Account Officer) mikro memerlukan keberanian turun ke desa/pasar; (4) integritas dalam pengelolaan dana. Kandidat yang menonjol biasanya yang memiliki pengalaman sosial atau komunitas dan dapat menghubungkan nilai pelayanan BRI dengan pengalaman pribadi mereka.`,
		track: 'corporate' as const,
		defaultAvatarId: 'avatar_professional_man'
	},
	{
		name: 'Bank Negara Indonesia (BNI)',
		description:
			'Bank BUMN fokus pada segmen korporasi dan internasional. Dikenal sebagai bank dengan jaringan global terluas di antara bank BUMN Indonesia.',
		llmContext: `BNI memiliki budaya "Prihatin, Bangga, Optimis" dan nilai inti Integritas, Profesionalisme, Orientasi Pelanggan, Perbaikan Tiada Henti, dan Sinergi. Wawancara BNI menekankan: (1) orientasi global dan bisnis internasional — kandidat diharapkan familiar dengan transaksi ekspor-impor dan trade finance; (2) profesionalisme tinggi — penampilan, diksi, dan struktur jawaban sangat diperhatikan; (3) kemampuan analisis risiko kredit; (4) leadership potential untuk program Officer Development Program (ODP). Pewawancara BNI dikenal formal dan terstruktur. Jawaban harus ringkas, terukur, dan profesional.`,
		track: 'corporate' as const,
		defaultAvatarId: 'avatar_professional_man'
	},
	{
		name: 'PT Pertamina (Persero)',
		description:
			'Perusahaan energi nasional terbesar Indonesia. Bergerak di hulu-hilir migas, energi baru terbarukan, dan petrokimia.',
		llmContext: `Pertamina memiliki nilai 6C: Clean, Competitive, Confident, Customer Focus, Commercial, Capable. Wawancara Pertamina sangat kompetitif karena rasio pelamar:posisi yang sangat tinggi. Fokus utama: (1) pemahaman industri energi Indonesia — kandidat harus tahu isu ketahanan energi nasional, transisi EBT, dan posisi Pertamina secara geopolitik; (2) safety culture — Pertamina sangat serius soal K3 (Keselamatan dan Kesehatan Kerja); (3) leadership dan pengalaman organisasi yang kuat; (4) kemampuan inovasi — Pertamina mendorong inisiatif digital dan efisiensi. Kandidat dari teknik, ekonomi, dan hukum sama-sama memiliki peluang namun harus menunjukkan relevansi langsung dengan bisnis Pertamina.`,
		track: 'corporate' as const,
		defaultAvatarId: 'avatar_hassan'
	},
	{
		name: 'PT PLN (Persero)',
		description:
			'Perusahaan listrik negara yang mengelola pembangkit, transmisi, dan distribusi listrik seluruh Indonesia.',
		llmContext: `PLN memiliki visi menjadi perusahaan listrik terkemuka se-Asia Tenggara dan pelopor transisi energi. Wawancara PLN berfokus: (1) komitmen terhadap misi layanan publik — listrik adalah kebutuhan dasar, kandidat harus memahami tanggung jawab sosial ini; (2) ketahanan mental untuk penugasan di daerah terpencil (3T) — PLN membuka posisi di seluruh Indonesia termasuk wilayah 3T; (3) pemahaman teknis kelistrikan untuk posisi teknik; (4) nilai AKHLAK BUMN. Pewawancara PLN sering menguji komitmen jangka panjang kandidat dan kesediaan ditempatkan di mana saja.`,
		track: 'corporate' as const,
		defaultAvatarId: 'avatar_hassan'
	},
	{
		name: 'Telkom Indonesia',
		description:
			'Perusahaan telekomunikasi dan teknologi digital terbesar di Indonesia. Induk dari Telkomsel dan berbagai anak perusahaan teknologi.',
		llmContext: `Telkom memiliki nilai "The Telkom Way" — Always The Best (Integrity, Enthusiasm, Totality) dan Always The Star (Solid, Speed, Smart). Budaya Telkom sangat agile dan digital-first. Wawancara Telkom berfokus: (1) mindset digital dan inovasi — kandidat harus antusias terhadap teknologi dan transformasi digital; (2) kolaborasi dan teamwork — Telkom bekerja dalam ekosistem besar; (3) kemampuan berpikir strategis tentang masa depan telekomunikasi; (4) growth mindset yang nyata dari pengalaman belajar mandiri. Kandidat yang menonjol biasanya memiliki portofolio proyek digital, kontribusi open source, atau pengalaman startup.`,
		track: 'corporate' as const,
		defaultAvatarId: 'avatar_young_man'
	},
	{
		name: 'PT Kereta Api Indonesia (KAI)',
		description:
			'Operator transportasi kereta api nasional. Mengelola seluruh perkeretaapian di Pulau Jawa, Sumatera, Sulawesi, dan Kalimantan.',
		llmContext: `KAI memiliki nilai 5 Pilar: Integritas, Profesional, Keselamatan, Inovasi, dan Pelayanan Prima. Safety adalah nilai absolut di KAI — tidak ada kompromi. Wawancara KAI menekankan: (1) komitmen terhadap keselamatan dan prosedur — kandidat harus memahami bahwa SOP adalah harga mati di industri perkeretaapian; (2) orientasi pelayanan publik yang tulus; (3) disiplin dan ketepatan waktu sebagai cerminan budaya KAI; (4) kemampuan bekerja dalam sistem yang terstruktur. Pewawancara KAI biasanya tenang namun detail dalam menggali pemahaman kandidat tentang keselamatan.`,
		track: 'corporate' as const,
		defaultAvatarId: 'avatar_professional_man'
	},

	// ─── SWASTA — TEKNOLOGI & STARTUP ───────────────────────────
	{
		name: 'Gojek / GoTo',
		description:
			'Super app teknologi terbesar Indonesia. Ekosistem mencakup transportasi, pengiriman, e-commerce, dan fintech.',
		llmContext: `GoTo memiliki nilai "GoTo DNA": Speed (bias for action), Ownership (think like an owner), Impact (customer obsession), Collaboration, dan Integrity. Wawancara GoTo sangat berbeda dari korporat tradisional — lebih informal namun sangat menuntut kedalaman berpikir. Fokus: (1) problem-solving dengan data — kandidat sering diminta menganalisis masalah nyata GoTo secara real-time; (2) ownership mindset — "apa yang akan kamu lakukan jika ini adalah bisnismu sendiri?"; (3) customer obsession — setiap keputusan dikembalikan ke dampak bagi pengguna; (4) ketidaknyamanan dengan ambiguitas — startup tidak memiliki jawaban pasti. Kandidat terbaik datang dengan riset mendalam tentang bisnis GoTo dan pertanyaan cerdas untuk pewawancara.`,
		track: 'corporate' as const,
		defaultAvatarId: 'avatar_young_man'
	},
	{
		name: 'Tokopedia',
		description:
			'Platform e-commerce terbesar Indonesia. Kini bagian dari ekosistem TikTok Shop setelah merger dengan TikTok.',
		llmContext: `Tokopedia memiliki DNA "Always Be Curious, Always Be Learning" dengan nilai inti Make It Happen, Make It Better, Make It Last. Budaya sangat data-driven dan meritokratis. Wawancara Tokopedia menekankan: (1) analytical thinking — kandidat harus nyaman dengan angka dan bisa membuat keputusan berbasis data; (2) growth mindset yang terbukti — bukan hanya klaim tapi ada portofolio atau cerita konkret; (3) customer centricity dalam setiap keputusan produk; (4) kemampuan berkolaborasi lintas fungsi (cross-functional). Proses seleksi biasanya multi-tahap dengan case study yang kompleks.`,
		track: 'corporate' as const,
		defaultAvatarId: 'avatar_young_man'
	},
	{
		name: 'Astra International',
		description:
			'Konglomerat multinasional Indonesia terbesar. Bergerak di otomotif, jasa keuangan, alat berat, agribisnis, infrastruktur, dan teknologi informasi.',
		llmContext: `Astra memiliki filosofi "Catur Dharma" — Menjadi Milik yang Bermanfaat, Memberikan Pelayanan Terbaik, Menghargai Individu, dan Berusaha Mencapai yang Terbaik. Budaya Astra sangat terstruktur, berbasis kompetensi, dan berorientasi jangka panjang. Wawancara Astra (terutama ADP — Astra Development Program) sangat ketat: (1) leadership competency yang terbukti dalam organisasi; (2) integritas tanpa kompromi — Astra memiliki rekam jejak etika bisnis yang kuat; (3) kemampuan analitis dan strategis; (4) komitmen untuk berkembang bersama perusahaan (bukan job-hopper). Kandidat Astra biasanya dari universitas top dengan rekam jejak organisasi yang solid.`,
		track: 'corporate' as const,
		defaultAvatarId: 'avatar_professional_man'
	},
	{
		name: 'Unilever Indonesia',
		description:
			'Perusahaan FMCG (Fast-Moving Consumer Goods) multinasional terbesar di Indonesia. Memiliki ratusan brand konsumen ikonik.',
		llmContext: `Unilever memiliki "Compass Strategy" dengan purpose "Making Sustainable Living Commonplace." Nilai inti: Integrity, Respect, Responsibility, Pioneering. Wawancara Unilever sangat terstruktur dengan metode STAR yang ketat. Fokus: (1) leadership dengan dampak nyata — bukan sekadar jabatan tapi perubahan yang dibuat; (2) sustainability mindset — kandidat harus memahami dan peduli pada isu lingkungan dan sosial; (3) consumer understanding — empati mendalam terhadap kebutuhan konsumen Indonesia; (4) kemampuan eksekusi di tengah kompleksitas organisasi besar. Unilever sangat menghargai kandidat yang bisa menyeimbangkan ambisi pribadi with purpose yang lebih besar.`,
		track: 'corporate' as const,
		defaultAvatarId: 'avatar_professional_man'
	},

	// ─── INSTANSI KEDINASAN ───────────────────────────────────────
	{
		name: 'Akademi Militer (Akmil)',
		description:
			'Lembaga pendidikan tinggi militer TNI Angkatan Darat. Mencetak perwira TNI AD yang profesional, bermoral, dan bela negara.',
		llmContext: `Akmil adalah salah satu seleksi paling berat di Indonesia. Proses Pantukhir (Panitia Penentuan Akhir) mencakup wawancara Mental Ideologi (MI) yang bersifat ELIMINATIF — satu jawaban yang tidak konsisten bisa langsung menggugurkan kandidat. Konteks wawancara MI Akmil: (1) pengujian ideologi Pancasila dan NKRI — kandidat harus mampu menjelaskan dan mempertahankan pandangan tentang ideologi negara dengan argumen yang kuat dan konsisten; (2) loyalitas absolut terhadap NKRI, TNI, and institusi — tidak ada ruang untuk keraguan; (3) ketahanan mental di bawah tekanan ekstrem — pewawancara SENGAJA menekan, memojokkan, dan menguji emosi kandidat; (4) konsistensi argumen — jawaban yang berbeda di pertanyaan berbeda namun topik sama akan langsung ditandai; (5) integritas dan moral — riwayat hidup akan digali secara mendalam. Persona pewawancara Akmil biasanya formal, tegas, dan seringkali intimidatif sebagai bagian dari teknik seleksi psikologis.`,
		track: 'military' as const,
		defaultAvatarId: 'avatar_hassan'
	},
	{
		name: 'Akademi Kepolisian (Akpol)',
		description:
			'Lembaga pendidikan tinggi Polri untuk mencetak perwira Polri yang profesional, transparan, dan melayani masyarakat.',
		llmContext: `Akpol menggunakan pendekatan seleksi yang mirip Akmil namun dengan penekanan pada nilai-nilai kepolisian: Tribrata (Rastra Sewakottama, Nagara Janottama, Yana Anucasana) and Catur Prasetya. Wawancara Akpol berfokus: (1) motivasi menjadi polisi yang tulus dan berbasis pelayanan masyarakat — bukan karena prestise atau keamanan kerja; (2) pemahaman hukum dan prosedur kepolisian; (3) integritas dan rekam jejak hidup yang bersih; (4) ketahanan mental dan kemampuan menghadapi situasi darurat; (5) kemampuan komunikasi dengan masyarakat dari berbagai latar belakang. Pewawancara Akpol akan menggali riwayat hidup kandidat secara sangat mendalam and mencari inkonsistensi.`,
		track: 'military' as const,
		defaultAvatarId: 'avatar_hassan'
	},
	{
		name: 'PKN STAN',
		description:
			'Politeknik Keuangan Negara STAN. Sekolah kedinasan di bawah Kementerian Keuangan yang mencetak aparatur negara di bidang keuangan negara.',
		llmContext: `PKN STAN memiliki seleksi yang sangat kompetitif dengan passing grade tertinggi di antara sekolah kedinasan. Wawancara PKN STAN berbeda dari MI militer — lebih fokus pada: (1) motivasi mengabdi di Kementerian Keuangan — kandidat harus bisa menjelaskan mengapa memilih karir di pengelolaan keuangan negara; (2) integritas dan anti-korupsi — Kemenkeu memiliki zero tolerance terhadap korupsi dan pewawancara akan menguji ini dengan skenario dilema etika; (3) pemahaman dasar keuangan negara, APBN, and perpajakan; (4) komitmen untuk belajar and bekerja keras di lingkungan birokrasi yang dinamis; (5) kemampuan analitis and ketelitian. Pewawancara STAN biasanya lebih tenang dari militer namun sangat detail and sering mengajukan pertanyaan "bagaimana jika" terkait integritas.`,
		track: 'stan' as const,
		defaultAvatarId: 'avatar_professional_man'
	},
	{
		name: 'CPNS Kemenkeu',
		description:
			'Seleksi Calon Pegawai Negeri Sipil Kementerian Keuangan. Mencakup DJP, DJBC, DJA, DJPB, and unit eselon 1 lainnya.',
		llmContext: `Kementerian Keuangan dikenal sebagai salah satu kementerian dengan budaya kerja paling profesional di Indonesia. Wawancara CPNS Kemenkeu sangat menekankan: (1) motivasi pelayanan publik yang genuine — bukan sekadar alasan "PNS aman and tunjangan besar"; (2) pemahaman fungsi unit yang dilamar (misal: DJP untuk pajak, DJBC untuk bea cukai); (3) integritas and pemahaman konflik kepentingan — Kemenkeu sangat serius dengan kode etik; (4) kompetensi teknis yang relevan dengan posisi; (5) kemampuan adaptasi dengan regulasi yang terus berubah. Kandidat yang menonjol selalu menghubungkan motivasi mereka dengan dampak nyata pada keuangan negara.`,
		track: 'civil_service' as const,
		defaultAvatarId: 'avatar_professional_man'
	},
	{
		name: 'CPNS Kemendagri',
		description:
			'Seleksi CPNS Kementerian Dalam Negeri. Mengelola otonomi daerah, administrasi kependudukan, and pemerintahan daerah.',
		llmContext: `Kemendagri berfokus pada pengelolaan pemerintahan dalam negeri and hubungan pusat-daerah. Wawancara CPNS Kemendagri menekankan: (1) pemahaman sistem otonomi daerah and desentralisasi fiskal; (2) komitmen pelayanan publik di daerah — kandidat harus siap ditempatkan di seluruh Indonesia; (3) kemampuan koordinasi and negosiasi antar instansi; (4) pemahaman regulasi pemerintahan daerah; (5) netralitas ASN — kandidat harus menunjukkan pemahaman tentang ASN yang tidak berpihak pada kepentingan politik. Wawancara biasanya lebih relaxed dari kementerian teknis namun tetap menguji kompetensi and motivasi secara mendalam.`,
		track: 'civil_service' as const,
		defaultAvatarId: 'avatar_professional_man'
	}
];

// ============================================================
// DATA POSISI per INSTITUSI
// (key: nama institusi → array posisi)
// ============================================================

const positionsByInstitution: Record<
	string,
	Array<{ name: string; description: string; llmContext: string }>
> = {
	'Bank Mandiri': [
		{
			name: 'Officer Development Program (ODP)',
			description:
				'Program pengembangan officer Mandiri untuk calon pemimpin masa depan. Rotasi di berbagai divisi selama 12 bulan.',
			llmContext:
				'ODP adalah jalur fast-track kepemimpinan Mandiri. Kandidat idealnya memiliki IPK ≥3.00, aktif organisasi, dan mampu menunjukkan leadership impact nyata. Pertanyaan akan banyak menguji kemampuan memimpin tim, mengelola konflik, dan mengambil keputusan di bawah tekanan.'
		},
		{
			name: 'Frontliner / Teller',
			description:
				'Melayani transaksi nasabah di counter cabang. Wajah pertama Bank Mandiri bagi nasabah.',
			llmContext:
				'Posisi frontliner menekankan pada service excellence dan ketahanan menghadapi volume kerja tinggi. Pertanyaan berfokus pada pengalaman pelayanan, cara menangani nasabah sulit, dan ketelitian dalam mengelola uang.'
		},
		{
			name: 'Analis Kredit',
			description:
				'Menganalisis kelayakan kredit nasabah korporat dan komersial. Mengelola portofolio kredit dan memitigasi risiko.',
			llmContext:
				'Posisi ini membutuhkan kemampuan analitis keuangan yang kuat. Pertanyaan akan menguji pemahaman tentang laporan keuangan, rasio-rasio kredit, skenario risiko, dan pengalaman menganalisis bisnis.'
		},
		{
			name: 'Digital Banking Analyst',
			description:
				'Mengembangkan dan mengoptimalkan produk digital banking Mandiri. Berkolaborasi dengan tim teknologi dan bisnis.',
			llmContext:
				'Kandidat harus memahami tren digital banking, fintech landscape Indonesia, dan perilaku pengguna digital. Pertanyaan menguji kemampuan product thinking, data analysis, dan pemahaman UX.'
		}
	],
	'Bank Rakyat Indonesia (BRI)': [
		{
			name: 'Mantri / Account Officer Mikro',
			description:
				'Melayani nasabah UMKM dan mikro di lapangan. Menilai kelayakan kredit usaha kecil secara langsung.',
			llmContext:
				'Posisi Mantri adalah ujung tombak BRI di grassroot. Kandidat harus menunjukkan keberanian turun ke lapangan, kemampuan menilai karakter dan bisnis nasabah kecil, dan semangat memberdayakan ekonomi rakyat. Pertanyaan akan banyak menyentuh pengalaman berinteraksi dengan masyarakat ekonomi bawah.'
		},
		{
			name: 'Management Development Program (MDP)',
			description:
				'Program pengembangan manajer BRI. Jalur karir untuk lulusan terbaik yang akan menjadi pemimpin BRI.',
			llmContext:
				'MDP BRI mencari kandidat yang memahami bisnis perbankan dan memiliki jiwa kepemimpinan. Selain kompetensi teknis, BRI sangat mementingkan nilai melayani dan keberpihakan pada rakyat kecil dalam kepemimpinan kandidat.'
		},
		{
			name: 'Analis IT / Software Engineer',
			description:
				'Mengembangkan sistem perbankan digital BRI. Mendukung transformasi digital BRI menuju bank digital terdepan.',
			llmContext:
				'BRI tengah agresif bertransformasi digital. Kandidat teknologi harus memahami skala sistem BRI yang sangat besar (salah satu pengguna teknologi terbesar di Indonesia) dan tantangan mengembangkan sistem yang reliable untuk jutaan transaksi.'
		}
	],
	'Bank Negara Indonesia (BNI)': [
		{
			name: 'Officer Development Program (ODP) BNI',
			description:
				'Program pengembangan perwira BNI dengan rotasi di berbagai lini bisnis. Fokus pada perbankan korporat dan internasional.',
			llmContext:
				'ODP BNI sangat prestisius dan kompetitif. Kandidat harus memiliki pemahaman bisnis internasional, kemampuan bahasa Inggris yang baik, dan rekam jejak akademis dan organisasi yang kuat. Pertanyaan menguji kemampuan analitis, leadership, dan pemahaman industri perbankan.'
		},
		{
			name: 'Trade Finance Officer',
			description:
				'Mengelola transaksi perdagangan internasional nasabah korporat. Produk L/C, SKBDN, dan instrumen trade finance lainnya.',
			llmContext:
				'Posisi ini membutuhkan pemahaman mendalam tentang perdagangan internasional dan dokumen ekspor-impor. Pertanyaan menguji pengetahuan tentang Incoterms, UCP 600, dan pengalaman mengelola transaksi lintas batas.'
		},
		{
			name: 'Relationship Manager Korporat',
			description:
				'Mengelola hubungan dengan nasabah korporat besar. Menjual solusi perbankan komprehensif untuk kebutuhan bisnis korporasi.',
			llmContext:
				'RM Korporat adalah posisi senior yang membutuhkan kemampuan negosiasi tinggi, pemahaman bisnis korporat, dan jaringan relasi yang luas. Pertanyaan menguji strategi akuisisi nasabah, manajemen portofolio, dan kemampuan presentasi solusi finansial.'
		}
	],
	'PT Pertamina (Persero)': [
		{
			name: 'Engineer Upstream',
			description:
				'Bekerja di operasi hulu migas Pertamina. Eksplorasi, drilling, dan produksi minyak dan gas bumi.',
			llmContext:
				'Posisi upstream membutuhkan pemahaman teknis mendalam tentang operasi migas. Pertanyaan menguji pengetahuan teknik perminyakan/geologi, safety culture, dan kemampuan bekerja di lingkungan HSSE (Health, Safety, Security, Environment) yang ketat.'
		},
		{
			name: 'Management Trainee (MT) Pertamina',
			description:
				'Program MT Pertamina untuk lulusan terbaik dari berbagai disiplin ilmu. Rotasi di seluruh direktorat bisnis Pertamina.',
			llmContext:
				'MT Pertamina adalah salah satu program paling bergengsi di Indonesia. Persaingan sangat ketat. Kandidat harus menunjukkan understanding bisnis energi yang luas, leadership yang terbukti, dan passion terhadap ketahanan energi nasional.'
		},
		{
			name: 'Analis Keuangan & Investasi',
			description:
				'Menganalisis kelayakan investasi proyek-proyek energi Pertamina. Valuasi, financial modeling, dan manajemen risiko investasi.',
			llmContext:
				'Posisi ini membutuhkan kemampuan financial modeling yang kuat dan pemahaman valuasi proyek energi berskala besar. Pertanyaan menguji kemampuan DCF, IRR, NPV, skenario analisis, dan pemahaman tentang industri energi global.'
		}
	],
	'PT PLN (Persero)': [
		{
			name: 'Engineer Transmisi & Distribusi',
			description:
				'Mengelola sistem transmisi dan distribusi listrik. Memastikan keandalan pasokan listrik ke seluruh wilayah.',
			llmContext:
				'Posisi ini membutuhkan pemahaman sistem tenaga listrik yang mendalam. Safety adalah nilai absolut — pertanyaan akan selalu menyentuh pemahaman kandidat tentang prosedur K3 dan pengalaman mengelola risiko keselamatan.'
		},
		{
			name: 'Staf IT & Digital Transformation',
			description: 'Mendukung transformasi digital PLN menuju smart grid dan digital utility.',
			llmContext:
				'PLN sedang masif berinvestasi dalam digitalisasi. Kandidat IT harus memahami tantangan spesifik digitalisasi utilitas: skala yang sangat besar, keandalan yang tidak bisa dikompromikan, dan integrasi sistem warisan (legacy system).'
		},
		{
			name: 'Staf Pengembangan Energi Baru Terbarukan (EBT)',
			description:
				'Mengembangkan dan mengoperasikan pembangkit EBT PLN: PLTS, PLTA, PLTB, dan panas bumi.',
			llmContext:
				'Posisi EBT membutuhkan kandidat yang passionate tentang transisi energi dan memahami tantangan teknis dan regulasi EBT di Indonesia. Pertanyaan menguji pemahaman tentang intermittency, grid integration, dan kebijakan energi nasional.'
		}
	],
	'Telkom Indonesia': [
		{
			name: 'Software Engineer',
			description:
				'Mengembangkan produk dan platform digital Telkom Group. Bekerja dalam tim agile dengan teknologi terkini.',
			llmContext:
				'Wawancara teknis Telkom mencakup coding challenge dan system design. Kandidat harus menunjukkan pemahaman tentang distributed systems, scalability, dan best practices pengembangan software. Kultur sangat menghargai kontribusi open source dan pembelajaran mandiri.'
		},
		{
			name: 'Product Manager',
			description:
				'Memimpin pengembangan produk digital Telkom dari ideasi hingga launch. Berkolaborasi dengan engineering, design, dan bisnis.',
			llmContext:
				'PM Telkom harus memiliki kemampuan product thinking yang kuat dan pemahaman tentang ekosistem digital Indonesia. Pertanyaan menguji kemampuan prioritisasi, stakeholder management, dan pengambilan keputusan berbasis data dalam konteks produk telekomunikasi.'
		},
		{
			name: 'Data Analyst / Data Scientist',
			description:
				'Mengolah dan menganalisis data besar Telkom untuk insight bisnis dan pengembangan produk AI.',
			llmContext:
				'Telkom memiliki salah satu dataset telekomunikasi terbesar di Indonesia. Posisi ini membutuhkan kemampuan statistik, machine learning, dan storytelling data. Pertanyaan menguji metodologi analisis, pemilihan model, dan kemampuan mengkomunikasikan insight kepada stakeholder non-teknis.'
		}
	],
	'PT Kereta Api Indonesia (KAI)': [
		{
			name: 'Management Trainee (MT) KAI',
			description:
				'Program MT KAI untuk calon manajer masa depan. Rotasi di berbagai unit bisnis: operasional, komersial, dan keuangan.',
			llmContext:
				'MT KAI membutuhkan kandidat yang memahami bisnis transportasi publik dan berkomitmen pada safety culture KAI. Pertanyaan menguji pemahaman tentang industri perkeretaapian, kemampuan memimpin di lingkungan operasional yang safety-critical.'
		},
		{
			name: 'Masinis / Operator Kereta',
			description:
				'Mengoperasikan kereta api secara aman dan tepat waktu. Posisi operasional inti KAI.',
			llmContext:
				'Posisi Masinis membutuhkan komitmen safety yang absolut dan disiplin tinggi. Pertanyaan menguji pemahaman tentang prosedur operasi kereta, penanganan situasi darurat, dan kemampuan tetap tenang di bawah tekanan.'
		},
		{
			name: 'Customer Service / PPKA',
			description:
				'Melayani penumpang KAI dan memastikan pengalaman perjalanan yang nyaman dan aman.',
			llmContext:
				'Posisi CS KAI menekankan pada service excellence dan kemampuan menangani keluhan penumpang secara profesional. Pertanyaan berfokus pada pengalaman pelayanan, cara menangani situasi darurat yang melibatkan penumpang, dan pemahaman prosedur keselamatan stasiun.'
		}
	],
	'Gojek / GoTo': [
		{
			name: 'Product Manager',
			description:
				'Memimpin pengembangan fitur dan produk GoTo. Mengelola roadmap, prioritas, dan kolaborasi cross-functional.',
			llmContext:
				'Wawancara PM GoTo sangat mendalam dan bisa 4-5 tahap. Kandidat akan diminta melakukan product case study secara live: mendefinisikan masalah, mengidentifikasi solusi, dan memprioritaskan dengan framework yang jelas. Ownership mindset adalah kunci — kandidat harus berpikir seperti founder produknya.'
		},
		{
			name: 'Software Engineer (Backend/Frontend/Mobile)',
			description: 'Membangun sistem dan fitur GoTo yang melayani jutaan pengguna setiap hari.',
			llmContext:
				'Wawancara teknis GoTo mencakup coding problem, system design, dan behavioral interview. Skala sistem GoTo sangat besar — pertanyaan system design akan fokus pada distributed systems, reliability, dan performance. Kandidat diharapkan aktif mengidentifikasi edge case dan tradeoff.'
		},
		{
			name: 'Business Analyst / Strategy',
			description:
				'Menganalisis data bisnis GoTo untuk mendukung keputusan strategis. Berkolaborasi dengan C-level untuk inisiatif growth.',
			llmContext:
				'Posisi ini membutuhkan kemampuan analitis tajam dan pemahaman bisnis marketplace. Pertanyaan sering berbentuk business case: "Bagaimana kamu meningkatkan GMV GoPay 20% dalam 6 bulan?" Kandidat harus struktural, berbasis data, dan mampu melihat second-order effects.'
		}
	],
	Tokopedia: [
		{
			name: 'Product Manager Marketplace',
			description: 'Mengembangkan fitur marketplace Tokopedia untuk jutaan penjual dan pembeli.',
			llmContext:
				'Wawancara PM Tokopedia sangat data-driven. Kandidat harus familiar dengan metrics marketplace (GMV, take rate, NPS, seller retention) dan bisa menganalisis trade-off antara kepentingan penjual dan pembeli.'
		},
		{
			name: 'Growth Marketing Manager',
			description:
				'Merancang dan mengeksekusi strategi pertumbuhan pengguna dan transaksi Tokopedia.',
			llmContext:
				'Posisi Growth membutuhkan kombinasi kreativitas dan analytical rigor. Pertanyaan menguji pemahaman funnel, A/B testing, cohort analysis, dan pengalaman menjalankan kampanye growth yang terukur hasilnya.'
		},
		{
			name: 'Software Engineer',
			description:
				'Membangun platform e-commerce Tokopedia yang menangani jutaan transaksi harian.',
			llmContext:
				'Wawancara teknis Tokopedia fokus pada problem solving, system design untuk skala besar (high traffic, high availability), dan culture fit dengan nilai "Make It Better". Kandidat diharapkan proaktif dalam mengidentifikasi masalah dan mengusulkan solusi.'
		}
	],
	'Astra International': [
		{
			name: 'Astra Development Program (ADP)',
			description:
				'Program pengembangan eksekutif muda Astra. Rotasi di berbagai lini bisnis group selama 2 tahun.',
			llmContext:
				'ADP adalah program paling bergengsi Astra. Seleksi sangat ketat (rasio bisa 1:100). Kandidat harus menunjukkan leadership yang terbukti, integritas tinggi, kemampuan analitis, dan visi jangka panjang. Astra menghargai kandidat yang punya genuine interest pada diversitas bisnis group mereka.'
		},
		{
			name: 'Staf Keuangan & Akuntansi',
			description:
				'Mengelola keuangan dan akuntansi unit bisnis Astra. Laporan keuangan, budgeting, dan kontrol internal.',
			llmContext:
				'Posisi keuangan Astra membutuhkan ketelitian tinggi dan pemahaman PSAK yang kuat. Integritas adalah non-negotiable — pertanyaan akan menguji pemahaman tentang internal control dan penanganan situasi etis yang ambigu.'
		},
		{
			name: 'Sales & Marketing Executive',
			description:
				'Menjual produk-produk Astra Group (otomotif, alat berat, dll) dan membangun hubungan dengan pelanggan.',
			llmContext:
				'Posisi sales Astra menekankan pada relationship building jangka panjang sesuai filosofi Catur Dharma. Pertanyaan menguji pengalaman penjualan, strategi membangun relasi, dan cara menangani penolakan dengan tetap profesional.'
		}
	],
	'Unilever Indonesia': [
		{
			name: 'Management Trainee (UFLP)',
			description:
				'Unilever Future Leaders Programme — jalur fast-track menjadi manajer Unilever dalam 3 tahun.',
			llmContext:
				'UFLP adalah salah satu MT paling kompetitif di Indonesia. Kandidat harus menunjukkan purpose-driven leadership, pemahaman tentang sustainability, dan kemampuan memimpin perubahan. Seleksi mencakup case study, psychometric test, dan interview panel.'
		},
		{
			name: 'Brand Manager',
			description:
				'Mengelola dan mengembangkan brand-brand Unilever di Indonesia. Strategi brand, kampanye iklan, dan inovasi produk.',
			llmContext:
				'Brand Manager Unilever harus memahami consumer insights secara mendalam. Pertanyaan menguji kemampuan membangun brand strategy, menganalisis kompetitor, dan menjalankan kampanye yang efektif dengan anggaran yang optimal.'
		},
		{
			name: 'Supply Chain Analyst',
			description:
				'Mengoptimalkan rantai pasok Unilever Indonesia dari sourcing hingga distribusi.',
			llmContext:
				'Supply chain Unilever sangat kompleks dengan ribuan SKU dan jutaan titik distribusi. Pertanyaan menguji pemahaman tentang inventory management, demand forecasting, dan kemampuan problem-solving ketika ada disruption di supply chain.'
		}
	],
	'Akademi Militer (Akmil)': [
		{
			name: 'Taruna Akmil — Wawancara Mental Ideologi (MI)',
			description:
				'Tahap wawancara MI Pantukhir penerimaan Taruna Akademi Militer TNI AD. Sifat ELIMINATIF.',
			llmContext:
				'Wawancara MI Akmil adalah yang paling intens dalam seleksi ini. Pewawancara adalah perwira senior TNI AD. Topik utama: (1) Pancasila dan UUD 1945 — harus hafal, paham, dan mampu menjelaskan implementasinya; (2) motivasi masuk Akmil yang genuine dan terukur; (3) riwayat keluarga dan latar belakang sosial; (4) pandangan tentang ancaman NKRI; (5) komitmen pengabdian tanpa batas. Tekanan sangat tinggi — pewawancara sengaja memotong, memojokkan, dan menguji reaksi emosional kandidat. Kandidat yang panik, berubah argumen, atau menunjukkan kelemahan emosional akan langsung dieliminasi.'
		}
	],
	'Akademi Kepolisian (Akpol)': [
		{
			name: 'Karbol Akpol — Wawancara Psikologi & Kepribadian',
			description:
				'Tahap wawancara psikologi dan kepribadian penerimaan Karbol Akpol. Menilai kesesuaian kandidat dengan nilai-nilai Polri.',
			llmContext:
				'Wawancara Akpol menggabungkan penilaian psikologis dan nilai kepolisian. Fokus: (1) motivasi menjadi polisi yang tidak klise — pewawancara sangat terlatih mendeteksi jawaban yang dihafal; (2) pengalaman kepemimpinan dan menyelesaikan konflik; (3) pemahaman hukum dasar dan kode etik Polri; (4) kemampuan mengendalikan emosi saat dikonfrontasi; (5) kejujuran tentang riwayat hidup — kebohongan adalah penyebab eliminasi paling umum.'
		}
	],
	'PKN STAN': [
		{
			name: 'Mahasiswa PKN STAN — Seleksi Wawancara',
			description:
				'Tahap wawancara seleksi penerimaan mahasiswa baru PKN STAN. Menilai motivasi dan integritas calon mahasiswa.',
			llmContext:
				'Wawancara PKN STAN biasanya dilakukan oleh panitia dari Kemenkeu. Pertanyaan fokus: (1) motivasi memilih STAN dan jalur karir di Kemenkeu — harus spesifik dan genuine; (2) pemahaman dasar tentang keuangan negara dan fungsi unit-unit Kemenkeu (DJP, DJBC, DJA, DJPB); (3) integritas dan pemahaman tentang korupsi dalam konteks keuangan negara; (4) rencana pengembangan diri sebagai aparatur keuangan negara; (5) kemampuan akademis dan kesiapan menghadapi pendidikan STAN yang intensif.'
		}
	],
	'CPNS Kemenkeu': [
		{
			name: 'CPNS Direktorat Jenderal Pajak (DJP)',
			description:
				'Jabatan fungsional dan pelaksana di Direktorat Jenderal Pajak. Mengelola penerimaan pajak negara.',
			llmContext:
				'DJP adalah salah satu unit paling bergengsi di Kemenkeu. Kandidat harus memahami sistem perpajakan Indonesia (UU HPP, PPN, PPh), visi transformasi DJP, dan tantangan kepatuhan pajak. Pertanyaan integritas sangat ketat — DJP memiliki sejarah kasus pegawai bermasalah dan sangat waspada.'
		},
		{
			name: 'CPNS Direktorat Jenderal Bea dan Cukai (DJBC)',
			description:
				'Jabatan di Direktorat Jenderal Bea dan Cukai. Mengawasi dan memfasilitasi perdagangan internasional.',
			llmContext:
				'DJBC memiliki tugas unik: memfasilitasi perdagangan sekaligus menegakkan hukum. Kandidat harus memahami keseimbangan ini. Pertanyaan menguji pemahaman tentang prosedur kepabeanan, tantangan penyelundupan, dan cara menjaga integritas di lingkungan yang memiliki godaan tinggi.'
		}
	],
	'CPNS Kemendagri': [
		{
			name: 'CPNS Analis Kebijakan',
			description:
				'Jabatan fungsional analis kebijakan di Kemendagri. Menganalisis dan merumuskan kebijakan otonomi daerah.',
			llmContext:
				'Analis kebijakan Kemendagri harus memahami kompleksitas hubungan pusat-daerah Indonesia. Pertanyaan menguji pemahaman tentang desentralisasi, DAU/DAK, pemekaran wilayah, dan tantangan koordinasi dengan 500+ pemerintah daerah.'
		},
		{
			name: 'CPNS Pengelola Kependudukan',
			description:
				'Mengelola administrasi kependudukan dan catatan sipil. Mendukung program Dukcapil digital.',
			llmContext:
				'Posisi ini berhubungan langsung dengan pelayanan data kependudukan masyarakat. Pertanyaan berfokus pada orientasi pelayanan publik, pemahaman tentang sistem Dukcapil, dan komitmen menjaga kerahasiaan data pribadi masyarakat.'
		}
	]
};

// ============================================================
// MAIN SEED FUNCTION
// ============================================================

async function main() {
	console.log('🌱 Memulai seeding institusi dan posisi...\n');

	try {
		// ── 1. Seed Master Institutions ──────────────────────────────
		console.log('📦 Seeding master_institution...');

		const institutionIdMap: Record<string, string> = {};

		for (const inst of institutions) {
			const id = createId();
			institutionIdMap[inst.name] = id;

			await db.insert(schema.masterInstitution).values({
				id,
				name: inst.name,
				track: inst.track,
				description: inst.description,
				llmContext: inst.llmContext,
				defaultAvatarId: (inst as any).defaultAvatarId,
				logoUrl: null // Bisa diisi nanti via admin panel
			});

			console.log(`  ✅ ${inst.name}`);
		}

		console.log(`\n  Total institusi: ${institutions.length}\n`);

		// ── 2. Seed Master Positions ─────────────────────────────────
		console.log('📦 Seeding master_position...');

		let totalPositions = 0;

		for (const [institutionName, positions] of Object.entries(positionsByInstitution)) {
			const institutionId = institutionIdMap[institutionName];
			if (!institutionId) {
				console.warn(`  ⚠️  Institusi tidak ditemukan: ${institutionName}`);
				continue;
			}

			for (const pos of positions) {
				await db.insert(schema.masterPosition).values({
					id: createId(),
					institutionId,
					name: pos.name,
					description: pos.description,
					llmContext: pos.llmContext,
					isActive: true
				});
				totalPositions++;
			}

			console.log(`  ✅ ${institutionName} — ${positions.length} posisi`);
		}

		console.log(`\n  Total posisi: ${totalPositions}`);

		console.log('\n✅ Seeding institusi & posisi selesai!');
	} catch (e) {
		console.error('❌ Error saat seeding:', e);
		throw e;
	}

	process.exit(0);
}

main().catch((err) => {
	console.error('❌ Seeding gagal:', err);
	process.exit(1);
});
