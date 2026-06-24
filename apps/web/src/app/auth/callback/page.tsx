import { AuthCallbackClient } from "@/components/auth/login-card";

export default async function AuthCallbackPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>;
}) {
  const params = await searchParams;
  return <AuthCallbackClient token={params.token ?? null} />;
}
