"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { authApi } from "@/api/endpoints";
import { useAuthStore } from "@/stores/auth-store";
import { useThemeStore } from "@/stores/theme-store";
import { cn } from "@/lib/cn";

const userLinks = [
  { href: "/", label: "채팅" },
  { href: "/simulator", label: "시뮬레이터" },
  { href: "/projects", label: "프로젝트" },
  { href: "/ads", label: "광고" },
  { href: "/reports", label: "리포트" },
  { href: "/dashboard", label: "대시보드" },
  { href: "/billing", label: "요금제" },
  { href: "/settings", label: "설정" },
  { href: "/organization", label: "조직" },
];

const adminLinks = [
  { href: "/admin", label: "관리 홈" },
  { href: "/admin/users", label: "회원" },
  { href: "/admin/chats", label: "채팅 기록" },
];

export function AppShell({ children, admin = false }: { children: React.ReactNode; admin?: boolean }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, refreshToken, logout } = useAuthStore();
  const toggleTheme = useThemeStore((s) => s.toggle);
  const links = admin ? adminLinks : userLinks;

  async function handleLogout() {
    if (refreshToken) {
      try {
        await authApi.logout(refreshToken);
      } catch {
        /* ignore */
      }
    }
    logout();
    router.replace("/login");
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <header className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3">
          <div className="flex items-center gap-6">
            <Link href={admin ? "/admin" : "/"} className="text-lg font-bold text-brand-600">
              Click Me
            </Link>
            <nav className="hidden flex-wrap gap-1 md:flex">
              {links.map((l) => (
                <Link
                  key={l.href}
                  href={l.href}
                  className={cn(
                    "rounded-lg px-3 py-1.5 text-sm",
                    pathname === l.href || pathname.startsWith(l.href + "/")
                      ? "bg-brand-50 text-brand-700 dark:bg-brand-700/20 dark:text-brand-100"
                      : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800",
                  )}
                >
                  {l.label}
                </Link>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-2">
            <span className="hidden text-sm text-slate-500 sm:inline">{user?.name}</span>
            <Button variant="ghost" size="sm" onClick={toggleTheme}>
              테마
            </Button>
            {!admin && user?.role === "admin" && (
              <Link href="/admin">
                <Button variant="secondary" size="sm">
                  관리자
                </Button>
              </Link>
            )}
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              로그아웃
            </Button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
    </div>
  );
}
