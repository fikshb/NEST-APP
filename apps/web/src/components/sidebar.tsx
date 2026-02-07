"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Handshake,
  Users,
  Building2,
  FileText,
  Settings,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/deals", label: "Deals", icon: Handshake },
  { href: "/tenants", label: "Tenants", icon: Users },
  { href: "/units", label: "Units", icon: Building2 },
  { href: "/documents", label: "Document Library", icon: FileText },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 min-h-screen bg-white border-r border-line-soft flex flex-col">
      {/* Logo */}
      <div className="px-6 py-8">
        <h3 className="text-[22px] font-heading font-semibold text-teal-900">
          NestApp
        </h3>
        <p className="text-xs font-ui text-text-muted mt-1">
          Serviced Apartment Management
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3">
        {NAV_ITEMS.map((item) => {
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-input text-sm font-ui transition-colors mb-1",
                isActive
                  ? "bg-teal-900/5 text-teal-900 font-medium"
                  : "text-text-secondary hover:bg-neutral-softWhite hover:text-teal-900"
              )}
            >
              <Icon size={18} strokeWidth={1.8} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-6 py-6 border-t border-line-soft">
        <p className="text-[11px] font-ui text-text-muted">PRD v8.1</p>
      </div>
    </aside>
  );
}
