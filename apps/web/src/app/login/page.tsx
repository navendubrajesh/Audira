import { LoginCard } from "@/components/auth/login-card";
import { getEnabledProviders } from "@/lib/auth";

export default function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ dev?: string }>;
}) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-neutral-50 px-6">
      <LoginCardWrapper searchParams={searchParams} />
    </main>
  );
}

async function LoginCardWrapper({
  searchParams,
}: {
  searchParams: Promise<{ dev?: string }>;
}) {
  const params = await searchParams;
  const devMode = params.dev === "1" || process.env.NODE_ENV === "development";
  const providers = devMode ? [] : await getEnabledProviders();
  return <LoginCard devMode={devMode} providers={providers} />;
}
