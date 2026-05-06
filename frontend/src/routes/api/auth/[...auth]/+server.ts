import { auth } from "$lib/server/auth";

export const GET = ({ request }) => auth.handler(request);
export const POST = ({ request }) => auth.handler(request);
