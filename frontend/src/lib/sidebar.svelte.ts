export const sidebarState = $state({
	isOpen: false
});

export function toggleSidebar() {
	sidebarState.isOpen = !sidebarState.isOpen;
}
