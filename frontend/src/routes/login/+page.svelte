<script lang="ts">
	import { authClient } from '$lib/auth-client';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';

	let activeTab = $state(page.url.searchParams.get('tab') === 'register' ? 'register' : 'login');
	let email = $state('');
	let name = $state('');
	let password = $state('');
	let loading = $state(false);
	let error = $state<string | null>(null);

	async function handleSubmit() {
		loading = true;
		error = null;

		if (activeTab === 'register') {
			const { error: signUpError } = await authClient.signUp.email({
				email,
				password,
				name,
				callbackURL: '/onboarding'
			});
			if (signUpError) {
				error = signUpError.message || 'Pendaftaran gagal';
				loading = false;
			} else {
				await goto('/onboarding');
			}
		} else {
			const { error: signInError } = await authClient.signIn.email({
				email,
				password
			});
			if (signInError) {
				error = signInError.message || 'Masuk gagal';
				loading = false;
			} else {
				await goto('/dashboard');
			}
		}
	}

	async function loginWithGoogle() {
		await authClient.signIn.social({
			provider: 'google',
			callbackURL: '/dashboard'
		});
	}
</script>

<main
	class="relative flex min-h-screen flex-col items-center justify-center overflow-hidden p-margin"
>
	<!-- Branding Logo Above Card -->
	<div class="mb-lg flex flex-col items-center">
		<img alt="HiReady Logo" class="mb-10 h-24 w-auto" src="/logo.png" />
	</div>

	<!-- Auth Card -->
	<div
		class="z-10 w-full max-w-[440px] overflow-hidden rounded-lg bg-surface-container-lowest shadow-soft transition-all duration-300"
	>
		<!-- Tabs -->
		<div class="flex border-b border-outline-variant">
			<button
				class="flex-1 py-2 font-label-bold text-label-bold transition-colors {activeTab ===
				'register'
					? 'border-b-2 border-primary-container bg-surface-container-low text-primary-container'
					: 'text-outline hover:text-primary-container'}"
				onclick={() => (activeTab = 'register')}
			>
				Daftar
			</button>
			<button
				class="flex-1 py-2 font-label-bold text-label-bold transition-colors {activeTab === 'login'
					? 'border-b-2 border-primary-container bg-surface-container-low text-primary-container'
					: 'text-outline hover:text-primary-container'}"
				onclick={() => (activeTab = 'login')}
			>
				Masuk
			</button>
		</div>

		<!-- Form Area -->
		<div class="p-4 md:p-8">
			<form
				class="space-y-4"
				onsubmit={(e) => {
					e.preventDefault();
					handleSubmit();
				}}
			>
				{#if activeTab === 'register'}
					<div class="">
						<label class="mb-1 block font-label-bold text-label-bold text-on-surface" for="reg-name"
							>Nama Lengkap</label
						>
						<input
							class="px-md py-sm w-full rounded-lg border border-outline-variant bg-white font-body-md text-body-md transition-all placeholder:text-outline/50 focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 focus:outline-none"
							id="reg-name"
							placeholder="Andi Pratama"
							type="text"
							bind:value={name}
							required
						/>
					</div>
				{/if}

				<div class="">
					<label class="mb-1 block font-label-bold text-label-bold text-on-surface" for="email"
						>Email</label
					>
					<input
						class="px-md py-sm w-full rounded-lg border border-outline-variant bg-white font-body-md text-body-md transition-all placeholder:text-outline/50 focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 focus:outline-none"
						id="email"
						placeholder="nama@email.com"
						type="email"
						bind:value={email}
						required
					/>
				</div>

				<div class="">
					<label class="mb-1 block font-label-bold text-label-bold text-on-surface" for="password"
						>Password</label
					>
					<input
						class="px-md py-sm w-full rounded-lg border border-outline-variant bg-white font-body-md text-body-md transition-all placeholder:text-outline/50 focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 focus:outline-none"
						id="password"
						placeholder="••••••••"
						type="password"
						bind:value={password}
						required
					/>
				</div>

				{#if error}
					<p class="text-center text-sm text-error">{error}</p>
				{/if}

				<button
					class="px-xl mt-2 w-full rounded-full bg-primary-container py-2 font-label-bold text-label-bold text-on-primary transition-all duration-200 hover:bg-primary active:scale-95 disabled:opacity-50"
					type="submit"
					disabled={loading}
				>
					{loading
						? activeTab === 'register'
							? 'Mendaftar...'
							: 'Masuk...'
						: activeTab === 'register'
							? 'Buat Akun'
							: 'Masuk'}
				</button>
			</form>

			<div class="py-sm relative mt-4 flex items-center">
				<div class="grow border-t border-outline-variant"></div>
				<span class="mx-md shrink font-label-sm text-label-sm text-outline">atau</span>
				<div class="grow border-t border-outline-variant"></div>
			</div>

			<button
				onclick={loginWithGoogle}
				class="gap-md mt-4 flex w-full items-center justify-center rounded-full border border-outline-variant bg-white px-4 py-2 transition-all duration-200 hover:bg-surface-container-low active:scale-95"
			>
				<img
					alt="Google"
					class="h-5 w-5"
					src="https://lh3.googleusercontent.com/aida-public/AB6AXuAGp523apUKFHtHV1jyHw57oLJyx3vdfCH2EYvjgEbEedEKBGFpPpA8esngAOadDY8ikZrgdoAzfnjkjLIJ01eeT157R6uOtCMsRNv0GlmhxCUPx1PfVt8x4EAGiiRscrbeSgAJxyZZYdDaZJERzBg-5BkS8SDDOqojtaLs9S_ZqeWZpXxg7KMaJho5NZBmDmVMeNwBZL2UPC4n8pLVt7OzcPA5ndhXr-SEFf94hjkNmO4EAGF2e23iQ2joM35xdQGsx3tZbSCc3yQ"
				/>
				<span class="font-label-bold text-label-bold text-on-surface-variant"
					>Lanjutkan dengan Google</span
				>
			</button>
		</div>
	</div>

	<!-- Decorative Subtle Background Element -->
	<div class="pointer-events-none fixed bottom-0 left-0 -z-10 h-1/2 w-full overflow-hidden">
		<div
			class="absolute -bottom-24 -left-24 h-96 w-96 rounded-full bg-primary-container/5 blur-3xl"
		></div>
		<div class="absolute -right-24 -bottom-12 h-64 w-64 rounded-full bg-tertiary/5 blur-3xl"></div>
	</div>
</main>
