import { config } from 'dotenv';
config();

import * as schema from '../schema';
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';

const client = postgres(process.env.DATABASE_URL ?? '');
const db = drizzle(client, { schema });

async function main() {
	console.log('Sedang melakukan seeding...');

	try {
		// Seeding Professional Man
		await db
			.insert(schema.interviewAvatar)
			.values({
				id: 'avatar_professional_man',
				name: 'Pak Subarjo',
				track: 'corporate',
				glbUrl: 'face/professional-man/model.glb',
				thumbnailUrl: 'face/professional-man/thumbnail.png',
				ttsVoiceId: 'id-ID-ArdiNeural',
				ttsFriendlyParams: { rate: '+0%', pitch: '+0Hz', volume: '+0%' },
				ttsFormalParams: { rate: '-10%', pitch: '-5Hz', volume: '+0%' },
				ttsIntimidatingParams: { rate: '-20%', pitch: '-10Hz', volume: '+10%' },
				promptFriendly: `Kamu adalah pewawancara profesional bernama "Professional Man" yang ramah dan suportif.
Kamu mendorong kandidat untuk berbicara bebas dan merasa nyaman.
Gunakan bahasa yang hangat, berikan pujian singkat saat kandidat menjawab dengan baik,
dan ajukan pertanyaan lanjutan dengan nada yang mendukung.`,
				promptFormal: `Kamu adalah pewawancara profesional bernama "Professional Man" yang formal dan netral.
Kamu mengevaluasi kandidat secara objektif tanpa menunjukkan emosi.
Gunakan bahasa baku dan formal, jaga nada bicara tetap konsisten,
dan ajukan pertanyaan secara lugas tanpa basa-basi berlebihan.`,
				promptIntimidating: `Kamu adalah pewawancara profesional bernama "Professional Man" yang tegas dan penuh tekanan.
Kamu menguji ketahanan mental kandidat dengan pertanyaan yang tajam dan kritis.
Gunakan nada bicara yang serius, sesekali tantang jawaban kandidat,
dan tunjukkan skeptisisme jika jawaban terasa tidak meyakinkan.`,
				cameraConfig: { headHeightRatio: 0.82, distanceOffset: 1.0, lookAtOffset: 0.05 },
				isActive: true
			})
			.onConflictDoUpdate({
				target: schema.interviewAvatar.id,
				set: {
					cameraConfig: { headHeightRatio: 0.82, distanceOffset: 1.0, lookAtOffset: 0.05 }
				}
			});

		console.log('✅ Avatar "Professional Man" berhasil di-seed.');

		// Seeding Indra (Boy Character)
		await db
			.insert(schema.interviewAvatar)
			.values({
				id: 'avatar_young_man',
				name: 'Indra',
				track: 'corporate',
				glbUrl: 'face/boy/model.glb',
				thumbnailUrl: 'face/boy/thumbnail.png',
				ttsVoiceId: 'id-ID-ArdiNeural',
				// Pitch sedikit lebih tinggi untuk kesan lebih muda
				ttsFriendlyParams: { rate: '+5%', pitch: '+5Hz', volume: '+0%' },
				ttsFormalParams: { rate: '-5%', pitch: '+2Hz', volume: '+0%' },
				ttsIntimidatingParams: { rate: '-10%', pitch: '-2Hz', volume: '+10%' },
				promptFriendly: `Kamu adalah Indra, pewawancara muda yang energik dan ramah. 
Kamu ingin melihat potensi kreatif dan antusiasme kandidat.
Gunakan bahasa yang santai tapi tetap sopan, banyak gunakan kata-kata penyemangat,
dan tunjukkan ketertarikan pada ide-ide inovatif kandidat.`,
				promptFormal: `Kamu adalah Indra, seorang rekruter muda yang efisien dan to-the-point.
Kamu fokus pada kompetensi teknis dan logika kandidat.
Berbicaralah dengan jelas dan lugas, hindari pembicaraan yang tidak relevan,
dan tanyakan detail konkret mengenai pengalaman kandidat.`,
				promptIntimidating: `Kamu adalah Indra, pewawancara yang skeptis dan sangat teliti.
Kamu tidak mudah terkesan dengan jawaban yang bersifat teoritis.
Tantang setiap pernyataan kandidat dengan "Mengapa?", cari celah dalam argumen mereka,
dan perhatikan konsistensi jawaban mereka di bawah tekanan.`,
				cameraConfig: { headHeightRatio: 0.82, distanceOffset: 1.0, lookAtOffset: 0.05 },
				isActive: true
			})
			.onConflictDoUpdate({
				target: schema.interviewAvatar.id,
				set: {
					cameraConfig: { headHeightRatio: 0.82, distanceOffset: 1.0, lookAtOffset: 0.05 }
				}
			});

		console.log('✅ Avatar "Indra" (Young Professional) berhasil di-seed.');

		// Seeding Hassan
		await db
			.insert(schema.interviewAvatar)
			.values({
				id: 'avatar_hassan',
				name: 'Hassan',
				track: 'corporate',
				glbUrl: 'face/hassan/model.glb',
				thumbnailUrl: 'face/hassan/thumbnail.png',
				ttsVoiceId: 'id-ID-ArdiNeural',
				ttsFriendlyParams: { rate: '+0%', pitch: '+0Hz', volume: '+0%' },
				ttsFormalParams: { rate: '-10%', pitch: '-5Hz', volume: '+0%' },
				ttsIntimidatingParams: { rate: '-20%', pitch: '-10Hz', volume: '+10%' },
				promptFriendly: `Kamu adalah Hassan, pewawancara yang bijaksana dan empatik.
Kamu ingin memahami motivasi terdalam kandidat.
Gunakan bahasa yang tenang, berikan jeda yang cukup bagi kandidat untuk berpikir,
dan ajukan pertanyaan yang bersifat reflektif.`,
				promptFormal: `Kamu adalah Hassan, seorang manajer senior yang sangat berpengalaman dan berwibawa.
Kamu fokus pada integritas dan visi jangka panjang kandidat.
Berbicaralah dengan nada yang stabil dan rendah, gunakan kosakata yang presisi,
dan tanyakan bagaimana kandidat akan berkontribusi pada budaya perusahaan.`,
				promptIntimidating: `Kamu adalah Hassan, pewawancara yang sangat kritis terhadap detail dan konsistensi.
Kamu menguji kejujuran kandidat dengan membandingkan berbagai bagian dari jawaban mereka.
Jadilah sangat jeli, jangan ragu untuk menginterupsi jika jawaban terasa tidak sinkron,
dan perhatikan bahasa tubuh serta nada suara kandidat.`,
				cameraConfig: { headHeightRatio: 0.1, distanceOffset: 0.8, lookAtOffset: 0.0 },
				isActive: true
			})
			.onConflictDoUpdate({
				target: schema.interviewAvatar.id,
				set: {
					cameraConfig: { headHeightRatio: 0.1, distanceOffset: 0.8, lookAtOffset: 0.0 }
				}
			});

		console.log('✅ Avatar "Hassan" berhasil di-seed.');
	} catch (e) {
		console.error('❌ Gagal melakukan seeding avatar:', e);
		throw e;
	}

	console.log('\nSeeding selesai!');
	process.exit(0);
}

main().catch((err) => {
	console.error('Seeding gagal:', err);
	process.exit(1);
});
