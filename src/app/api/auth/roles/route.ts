import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { cookies } from "next/headers";
import jwt from "jsonwebtoken";

export const dynamic = "force-dynamic";

const JWT_SECRET = process.env.JWT_SECRET || process.env.AUTH_JWT_SECRET || "change-me-in-production";

export async function GET() {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("auth-token")?.value;

    if (!token) {
      return NextResponse.json({ role: null, authenticated: false });
    }

    try {
      const decoded = jwt.verify(token, JWT_SECRET) as any;
      const admin = await prisma.admin.findUnique({
        where: { id: decoded.userId },
        select: { id: true, username: true, role: true, isActive: true },
      });

      if (!admin || !admin.isActive) {
        return NextResponse.json({ role: null, authenticated: false });
      }

      return NextResponse.json({
        role: admin.role,
        username: admin.username,
        authenticated: true,
      });
    } catch {
      return NextResponse.json({ role: null, authenticated: false });
    }
  } catch (error) {
    return NextResponse.json({ role: null, authenticated: false });
  }
}

export async function POST(request: Request) {
  try {
    const { userId, role } = await request.json();
    const cookieStore = await cookies();
    const token = cookieStore.get("auth-token")?.value;

    if (!token) {
      return NextResponse.json(
        { success: false, error: "Not authenticated" },
        { status: 401 }
      );
    }

    const decoded = jwt.verify(token, JWT_SECRET) as any;
    
    // Only admins can change roles
    const currentUser = await prisma.admin.findUnique({
      where: { id: decoded.userId },
    });

    if (!currentUser || currentUser.role !== "admin") {
      return NextResponse.json(
        { success: false, error: "Unauthorized" },
        { status: 403 }
      );
    }

    // Update user role
    const updated = await prisma.admin.update({
      where: { id: parseInt(userId) },
      data: { role },
    });

    return NextResponse.json({ success: true, admin: updated });
  } catch (error: any) {
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

