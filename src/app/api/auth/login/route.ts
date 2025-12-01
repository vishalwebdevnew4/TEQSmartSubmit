import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";

const JWT_SECRET = process.env.JWT_SECRET || process.env.AUTH_JWT_SECRET || "change-me-in-production";
const JWT_EXPIRES_IN = process.env.AUTH_JWT_EXPIRES ?? "1h";

export async function POST(req: NextRequest) {
  try {
    const { username, password } = await req.json();

    if (!username || typeof username !== "string" || !password || typeof password !== "string") {
      return NextResponse.json({ detail: "Username and password are required." }, { status: 400 });
    }

    const admin = await prisma.admin.findUnique({
      where: { username },
    });

    if (!admin) {
      return NextResponse.json({ detail: "Incorrect username or password." }, { status: 401 });
    }

    const passwordValid = await bcrypt.compare(password, admin.passwordHash);
    if (!passwordValid) {
      return NextResponse.json({ detail: "Incorrect username or password." }, { status: 401 });
    }

    const accessToken = jwt.sign(
      {
        sub: admin.id,
        username: admin.username,
      },
      JWT_SECRET,
      {
        expiresIn: JWT_EXPIRES_IN,
      },
    );

    return NextResponse.json({
      access_token: accessToken,
      token_type: "bearer",
      user: {
        id: admin.id,
        username: admin.username,
      },
    });
  } catch (error) {
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to process login request." },
      { status: 500 },
    );
  }
}


