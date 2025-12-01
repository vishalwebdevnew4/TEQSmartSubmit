import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { headers } from "next/headers";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const { clientId, eventType, eventData, timeOnPage } = await request.json();
    const headersList = await headers();
    
    if (!clientId || !eventType) {
      return NextResponse.json(
        { success: false, error: "Missing clientId or eventType" },
        { status: 400 }
      );
    }

    // Get client
    const client = await prisma.client.findUnique({
      where: { id: parseInt(clientId) },
    });

    if (!client) {
      return NextResponse.json(
        { success: false, error: "Client not found" },
        { status: 404 }
      );
    }

    // Get IP and user agent
    const ipAddress = headersList.get("x-forwarded-for") || headersList.get("x-real-ip") || "unknown";
    const userAgent = headersList.get("user-agent") || "unknown";

    // Create tracking event
    const tracking = await prisma.clientTracking.create({
      data: {
        clientId: parseInt(clientId),
        eventType,
        eventData: eventData || {},
        timeOnPage: timeOnPage || null,
        ipAddress,
        userAgent,
      },
    });

    // Update client status based on event type
    const updates: any = {};
    if (eventType === "email_opened" && !client.emailOpenedAt) {
      updates.emailOpenedAt = new Date();
      updates.status = "opened";
    }
    if (eventType === "link_clicked" && !client.lastClickedAt) {
      updates.lastClickedAt = new Date();
      updates.status = "clicked";
    }
    if (eventType === "download" || eventType === "converted") {
      updates.status = "converted";
    }

    if (Object.keys(updates).length > 0) {
      await prisma.client.update({
        where: { id: parseInt(clientId) },
        data: updates,
      });
    }

    return NextResponse.json({ success: true, tracking });
  } catch (error: any) {
    console.error("Error tracking client event:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Failed to track event" },
      { status: 500 }
    );
  }
}

