import { NextResponse } from "next/server";
import { processTemplateWithBusinessData } from "./process-template-handler";

export const dynamic = "force-dynamic";

/**
 * Process template and inject business data
 */
export async function POST(request: Request) {
  try {
    const { templateCategory, templateName, businessData } = await request.json();

    if (!templateCategory || !templateName || !businessData) {
      return NextResponse.json(
        { success: false, error: "Missing required parameters" },
        { status: 400 }
      );
    }

    const result = await processTemplateWithBusinessData(
      templateCategory,
      templateName,
      businessData
    );

    return NextResponse.json(result);
  } catch (error: any) {
    console.error("Error processing template:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Failed to process template" },
      { status: 500 }
    );
  }
}

