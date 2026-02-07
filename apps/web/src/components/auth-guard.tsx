"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { isAuthenticated } from "@/lib/auth";
import { Sidebar } from "@/components/sidebar";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [checked, setChecked] = useState(false);
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    const auth = isAuthenticated();
    setAuthed(auth);
    setChecked(true);

    if (!auth && pathname !== "/login") {
      router.replace("/login");
    }
    if (auth && pathname === "/login") {
      router.replace("/");
    }
  }, [pathname, router]);

  if (!checked) return null;

  // Login page: no sidebar, full-width
  if (pathname === "/login") {
    return <>{children}</>;
  }

  // Not authenticated: don't render anything (redirect in progress)
  if (!authed) return null;

  // Authenticated: render with sidebar
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-6 lg:p-8 max-w-layout mx-auto w-full">
        {children}
      </main>
    </div>
  );
}
