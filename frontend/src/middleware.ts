import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PUBLIC = ["/login"];

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  if (PUBLIC.some((p) => pathname.startsWith(p))) {
    if (pathname === "/login" && req.cookies.get("clickme_auth")?.value === "1") {
      const role = req.cookies.get("clickme_role")?.value;
      const dest = role === "admin" ? "/admin" : "/";
      return NextResponse.redirect(new URL(dest, req.url));
    }
    return NextResponse.next();
  }

  if (req.cookies.get("clickme_auth")?.value !== "1") {
    return NextResponse.redirect(new URL("/login", req.url));
  }

  const role = req.cookies.get("clickme_role")?.value;
  if (pathname.startsWith("/admin") && role !== "admin") {
    return NextResponse.redirect(new URL("/", req.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|uploads).*)"],
};
