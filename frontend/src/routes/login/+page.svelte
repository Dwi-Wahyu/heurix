<script lang="ts">
	import { authClient } from '$lib/auth-client';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import logo from '$lib/assets/logo.png?enhanced';
	import loginArt from '$lib/assets/login-art.png?enhanced';

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
			const result = await authClient.signUp.email({
				email,
				password,
				name,
				callbackURL: '/onboarding'
			});
			if (result.error) {
				error = result.error.message || 'Pendaftaran gagal';
				loading = false;
			} else {
				await goto('/onboarding');
			}
		} else {
			const result = await authClient.signIn.email({
				email,
				password
			});
			if (result.error) {
				error = result.error.message || 'Masuk gagal';
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

<main class="flex min-h-screen w-full">
	<!-- Left Panel: Form Area -->
	<div class="relative flex w-full flex-col bg-white lg:w-1/2">
		<!-- Branding Logo Top Left -->
		<div class="absolute mt-6 flex w-full justify-center">
			<div class="flex flex-col items-center">
				<div class="flex items-end gap-1">
					<enhanced:img alt="Heurix Logo" class="h-10 w-auto" src={logo} />
					<span class="text-3xl font-extrabold tracking-tight text-primary"> eurix </span>
				</div>
				<p class="mt-1 text-xs font-medium text-gray-500">
					Experience the Pressure. Master the interview
				</p>
			</div>
		</div>

		<div class="flex flex-1 flex-col items-center justify-center p-6 sm:p-12">
			<!-- Auth Card -->
			<div
				class="z-10 w-full max-w-110 overflow-hidden rounded-lg bg-white shadow-lg transition-all duration-300"
			>
				<!-- Tabs -->
				<div class="flex border-b border-outline-variant">
					<button
						class="flex-1 px-4 py-3 font-label-bold text-label-bold transition-colors {activeTab ===
						'register'
							? 'border-b-4 border-primary-container bg-surface-container-low text-primary-container'
							: 'text-outline hover:text-primary-container'}"
						onclick={() => (activeTab = 'register')}
					>
						Daftar
					</button>
					<button
						class="flex-1 px-4 py-3 font-label-bold text-label-bold transition-colors {activeTab ===
						'login'
							? 'border-b-4 border-primary-container bg-surface-container-low text-primary-container'
							: 'text-outline hover:text-primary-container'}"
						onclick={() => (activeTab = 'login')}
					>
						Masuk
					</button>
				</div>

				<!-- Form Area -->
				<div class="p-6 md:p-8">
					<form
						class="space-y-4"
						onsubmit={(e) => {
							e.preventDefault();
							handleSubmit();
						}}
					>
						{#if activeTab === 'register'}
							<div class="">
								<label
									class="mb-1 block font-label-bold text-label-bold text-on-surface"
									for="reg-name">Nama Lengkap</label
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
							<label
								class="mb-1 block font-label-bold text-label-bold text-on-surface"
								for="password">Password</label
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
							class="px-xl mt-6 w-full rounded-full bg-primary-container py-3 font-label-bold text-label-bold text-on-primary transition-all duration-200 hover:bg-primary active:scale-95 disabled:opacity-50"
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

					<div class="py-sm relative mt-6 flex items-center">
						<div class="grow border-t border-outline-variant"></div>
						<span class="mx-md shrink font-label-sm text-label-sm text-outline">atau</span>
						<div class="grow border-t border-outline-variant"></div>
					</div>

					<button
						onclick={loginWithGoogle}
						class="gap-md mt-6 flex w-full items-center justify-center gap-2 rounded-full border border-outline-variant bg-white px-4 py-3 transition-all duration-200 hover:bg-surface-container-low active:scale-95"
					>
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 16 16"
							><g fill="none" fill-rule="evenodd" clip-rule="evenodd"
								><path
									fill="#f44336"
									d="M7.209 1.061c.725-.081 1.154-.081 1.933 0a6.57 6.57 0 0 1 3.65 1.82a100 100 0 0 0-1.986 1.93q-1.876-1.59-4.188-.734q-1.696.78-2.362 2.528a78 78 0 0 1-2.148-1.658a.26.26 0 0 0-.16-.027q1.683-3.245 5.26-3.86"
									opacity="0.987"
								/><path
									fill="#ffc107"
									d="M1.946 4.92q.085-.013.161.027a78 78 0 0 0 2.148 1.658A7.6 7.6 0 0 0 4.04 7.99q.037.678.215 1.331L2 11.116Q.527 8.038 1.946 4.92"
									opacity="0.997"
								/><path
									fill="#448aff"
									d="M12.685 13.29a26 26 0 0 0-2.202-1.74q1.15-.812 1.396-2.228H8.122V6.713q3.25-.027 6.497.055q.616 3.345-1.423 6.032a7 7 0 0 1-.51.49"
									opacity="0.999"
								/><path
									fill="#43a047"
									d="M4.255 9.322q1.23 3.057 4.51 2.854a3.94 3.94 0 0 0 1.718-.626q1.148.812 2.202 1.74a6.62 6.62 0 0 1-4.027 1.684a6.4 6.4 0 0 1-1.02 0Q3.82 14.524 2 11.116z"
									opacity="0.993"
								/></g
							></svg
						>
						<span class="font-label-bold text-label-bold text-on-surface-variant"
							>Lanjutkan dengan Google</span
						>
					</button>
				</div>
			</div>
		</div>
	</div>

	<!-- Right Panel: Decorative Image Panel -->
	<div class="relative hidden bg-[#7a0c16] lg:block lg:w-1/2">
		<!-- Fallback pattern background if image doesn't exist -->
		<div
			class="absolute inset-0 opacity-10"
			style="background-image: radial-gradient(white 1px, transparent 1px); background-size: 20px 20px;"
		></div>

		<!-- Main illustration/artwork specified by user (needs to be present in static folder) -->
		<enhanced:img
			src={loginArt}
			alt="Heurix Dashboard Art"
			class="absolute inset-0 h-full w-full object-cover object-center"
		/>
	</div>
</main>
