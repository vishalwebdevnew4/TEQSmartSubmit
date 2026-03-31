import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const key = searchParams.get("key");

    if (key) {
      const setting = await prisma.setting.findUnique({
        where: { key },
      });

      if (!setting) {
        return NextResponse.json({ detail: "Setting not found." }, { status: 404 });
      }

      return NextResponse.json(setting);
    }

    const settings = await prisma.setting.findMany({
      orderBy: {
        key: "asc",
      },
    });

    return NextResponse.json(settings);
  } catch (error) {
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to fetch settings." },
      { status: 500 }
    );
  }
}

export async function PUT(req: NextRequest) {
  try {
    const body = await req.json();
    const { key, value } = body;

    if (!key || typeof key !== "string") {
      return NextResponse.json({ detail: "Key is required." }, { status: 400 });
    }

    if (value === undefined) {
      return NextResponse.json({ detail: "Value is required." }, { status: 400 });
    }

    const setting = await prisma.setting.upsert({
      where: { key },
      update: { value: String(value) },
      create: { key, value: String(value) },
    });

    return NextResponse.json(setting);
  } catch (error) {
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to update setting." },
      { status: 500 }
    );
  }
}

