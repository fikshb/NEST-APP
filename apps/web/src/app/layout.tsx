import type { Metadata } from "next";
import { Sidebar } from "@/components/sidebar";
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
          <div className="flex min-h-screen">
            <Sidebar />
            <main className="flex-1 p-6 lg:p-8 max-w-layout mx-auto w-full">
              {children}
            </main>
          </div>
        </QueryProvider>
      </body>
    </html>
  );
}
