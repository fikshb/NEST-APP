import type { Metadata } from "next";
import { AuthGuard } from "@/components/auth-guard";
import { QueryProvider } from "@/lib/query-provider";
import "./globals.css";

export const metadata: Metadata = {
  title: "NestApp — Serviced Apartment Management",
  description: "PRD v8.1 — Operational management for NEST Serviced Apartment",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <QueryProvider>
          <AuthGuard>{children}</AuthGuard>
        </QueryProvider>
      </body>
    </html>
  );
}
