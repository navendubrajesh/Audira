import Link from "next/link";

export default function AccessDeniedPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-neutral-50 px-6 text-center">
      <h1 className="text-2xl font-bold text-neutral-900">Access not authorised</h1>
      <p className="mt-3 max-w-md text-neutral-600">
        Your account does not have permission to view this resource. Contact your
        administrator if you believe this is an error.
      </p>
      <Link
        href="/"
        className="mt-6 text-sm font-medium text-brand-600 hover:text-brand-700"
      >
        Return to home
      </Link>
    </main>
  );
}
