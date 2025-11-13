import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import bcrypt from "bcryptjs";

const ADMIN_TOKEN = process.env.TEQ_ADMIN_REGISTRATION_TOKEN;

export async function POST(req: NextRequest) {
  try {
    const adminTokenHeader = req.headers.get("x-admin-token");
    if (!ADMIN_TOKEN || adminTokenHeader !== ADMIN_TOKEN) {
      return NextResponse.json({ detail: "Invalid admin registration token." }, { status: 403 });
    }

    const { username, password } = await req.json();

    if (!username || typeof username !== "string" || !password || typeof password !== "string") {
      return NextResponse.json({ detail: "Username and password are required." }, { status: 400 });
    }

    const existing = await prisma.admin.findUnique({
      where: { username },
    });

    if (existing) {
      return NextResponse.json({ detail: "Username already exists." }, { status: 409 });
    }

    const hashedPassword = await bcrypt.hash(password, 12);

    await prisma.admin.create({
      data: {
        username,
        passwordHash: hashedPassword,
      },
    });

    return NextResponse.json({ status: "success" }, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to register admin." },
      { status: 500 },
    );
  }
}


