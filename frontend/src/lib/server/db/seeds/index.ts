import { config } from 'dotenv';
config();

import * as schema from '../schema';
import * as authSchema from '../auth.schema';
import { Faker, id_ID } from '@faker-js/faker';
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';

const faker = new Faker({ locale: [id_ID] });

import { betterAuth } from 'better-auth';
import { drizzleAdapter } from 'better-auth/adapters/drizzle';

if (process.env.DATABASE_URL) {
	console.log('stop');
}

const client = postgres(process.env.DATABASE_URL ?? '');
const db = drizzle(client, { schema });

export const auth = betterAuth({
	baseURL: process.env.ORIGIN,
	secret: process.env.BETTER_AUTH_SECRET,
	database: drizzleAdapter(db, { provider: 'mysql' }),
	emailAndPassword: { enabled: true },
	plugins: []
});

async function main() {
	console.log('Sedang melakukan seeding...');

	try {
	} catch (e) {}

	console.log('\nSeeding selesai!');
	process.exit(0);
}

main().catch((err) => {
	console.error('Seeding gagal:', err);
	process.exit(1);
});
