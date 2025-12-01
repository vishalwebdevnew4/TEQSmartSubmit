import { NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";
import { prisma } from "@/lib/prisma";
import fs from "fs/promises";
import { tmpdir } from "os";
import { processTemplateWithBusinessData } from "../process-template-handler";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const { businessId, copyStyle = "friendly", templateCategory, templateName } = await request.json();

    if (!businessId) {
      return NextResponse.json(
        { success: false, error: "Missing businessId" },
        { status: 400 }
      );
    }

    // Fetch business data
    const business = await prisma.business.findUnique({
      where: { id: parseInt(businessId) },
    });

    if (!business) {
      return NextResponse.json(
        { success: false, error: "Business not found" },
        { status: 404 }
      );
    }

    // Prepare business data for Python service
    const businessData = {
      name: business.name,
      phone: business.phone,
      address: business.address,
      website: business.website,
      description: business.description,
      categories: business.categories || [],
      email: business.website ? `contact@${business.website.replace(/^https?:\/\//, '').split('/')[0]}` : undefined,
    };

    // Declare templateFiles at the top level
    let templateFiles: Record<string, string> = {};

    // If template is selected, process it with business data
    if (templateCategory && templateName) {
      try {
        // Process template with business data
        const processed = await processTemplateWithBusinessData(
          templateCategory,
          templateName,
          businessData
        );

        if (processed.success) {
          // Use processed template instead of Python generator
          templateFiles = {
            "index.html": processed.html,
            "about.html": processed.dynamicPages?.about || "",
            "contact.html": processed.dynamicPages?.contact || "",
          };
          
          // Create template version with processed content
          const existingTemplate = await prisma.template.findFirst({
            where: {
              businessId: business.id,
              name: {
                startsWith: `${business.name} - Website Template`,
              },
            },
          });

          let template;
          if (existingTemplate) {
            template = await prisma.template.update({
              where: { id: existingTemplate.id },
              data: {
                description: `Generated website for ${business.name} using ${templateName} template`,
                updatedAt: new Date(),
              },
            });
          } else {
            const baseName = `${business.name} - Website Template`;
            let templateNameUnique = baseName;
            let counter = 1;
            
            while (await prisma.template.findUnique({ where: { name: templateNameUnique } })) {
              templateNameUnique = `${baseName} (${counter})`;
              counter++;
            }
            
            template = await prisma.template.create({
              data: {
                name: templateNameUnique,
                description: `Generated website for ${business.name} using ${templateName} template`,
                fieldMappings: {},
                businessId: business.id,
              },
            });
          }

          const existingVersions = await prisma.templateVersion.count({
            where: { templateId: template.id },
          });

          const templateVersion = await prisma.templateVersion.create({
            data: {
              templateId: template.id,
              version: existingVersions + 1,
              content: {
                ...templateFiles,
                _metadata: {
                  templateSource: `${templateCategory}/${templateName}`,
                  logoUrl: processed.logoUrl,
                  generatedAt: new Date().toISOString(),
                  copyStyle: copyStyle,
                },
              },
              colorPalette: {},
              typography: {},
              aiCopyStyle: copyStyle,
              isActive: true,
            },
          });

          await prisma.templateVersion.updateMany({
            where: {
              templateId: template.id,
              id: { not: templateVersion.id },
            },
            data: { isActive: false },
          });

          return NextResponse.json({
            success: true,
            templateId: template.id,
            templateVersionId: templateVersion.id,
            isGptGenerated: false,
            templateSource: `${templateCategory}/${templateName}`,
          });
        }
      } catch (error) {
        console.error("Error processing template:", error);
        // Fall through to Python generator as fallback
      }
    }

    // Call Python website generator
    const scriptPath = path.join(process.cwd(), "backend", "app", "services", "website_generator.py");
    const tempDir = path.join(tmpdir(), `website-${businessId}-${Date.now()}`);

    // Pass environment variables to Python process
    const env = {
      ...process.env,
      // Ensure API keys are passed
      OPENAI_API_KEY: process.env.OPENAI_API_KEY || "",
      GOOGLE_AI_API_KEY: process.env.GOOGLE_AI_API_KEY || "",
      HUGGINGFACE_API_KEY: process.env.HUGGINGFACE_API_KEY || "",
      ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY || "",
    };

    const pythonProcess = spawn(
      "python",
      [
        scriptPath,
        "--business-data",
        JSON.stringify(businessData),
        "--style",
        copyStyle,
        "--output",
        tempDir,
      ],
      {
        cwd: process.cwd(),
        stdio: ["pipe", "pipe", "pipe"],
        env: env,
      }
    );

    let stdout = "";
    let stderr = "";

    pythonProcess.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    const result = await new Promise<{ success: boolean; data?: any; error?: string }>((resolve) => {
      pythonProcess.on("close", (code) => {
        if (code === 0) {
          try {
            const data = JSON.parse(stdout);
            resolve({ success: true, data });
          } catch (e) {
            resolve({ success: false, error: "Failed to parse response" });
          }
        } else {
          resolve({ success: false, error: stderr || "Python script failed" });
        }
      });
    });

    if (!result.success) {
      return NextResponse.json(
        { success: false, error: result.error },
        { status: 500 }
      );
    }

    // Get template files from Python script response or read from disk
    // First, try to get content from Python script response
    if (result.data?.content && typeof result.data.content === "object") {
      templateFiles = result.data.content;
    } else {
      // Fallback: Read files from temp directory
      try {
        const files = await fs.readdir(tempDir, { recursive: true });
        for (const file of files) {
          const filePath = path.join(tempDir, file);
          const stats = await fs.stat(filePath);
          if (stats.isFile()) {
            const content = await fs.readFile(filePath, "utf-8");
            templateFiles[file] = content;
          }
        }
      } catch (error) {
        console.error("Error reading template files:", error);
      }
    }
    
    // Ensure we have content - if still empty, log error
    if (Object.keys(templateFiles).length === 0) {
      console.error("No template files found! Python response:", result.data);
    }

    // Check if GPT was used (from Python script response)
    const isGptGenerated = result.data?.isGptGenerated === true || 
                          (result.data?.content && Object.keys(result.data.content).length > 0 && 
                           result.data.content["app/page.tsx"] && 
                           result.data.content["app/page.tsx"].length > 1000);

    // Create template version in database
    // Check if template already exists for this business
    const existingTemplate = await prisma.template.findFirst({
      where: {
        businessId: business.id,
        name: {
          startsWith: `${business.name} - Website Template`,
        },
      },
    });

    let template;
    if (existingTemplate) {
      // Update existing template
      template = await prisma.template.update({
        where: { id: existingTemplate.id },
        data: {
          description: `Generated website for ${business.name}`,
          updatedAt: new Date(),
        },
      });
    } else {
      // Create new template with unique name
      const baseName = `${business.name} - Website Template`;
      let templateName = baseName;
      let counter = 1;
      
      // Ensure unique name
      while (await prisma.template.findUnique({ where: { name: templateName } })) {
        templateName = `${baseName} (${counter})`;
        counter++;
      }
      
      template = await prisma.template.create({
        data: {
          name: templateName,
          description: `Generated website for ${business.name}`,
          fieldMappings: {},
          businessId: business.id,
        },
      });
    }

    // Get next version number
    const existingVersions = await prisma.templateVersion.count({
      where: { templateId: template.id },
    });

    // Store GPT status in content metadata
    const contentWithMetadata = {
      ...templateFiles,
      _metadata: {
        isGptGenerated,
        generatedAt: new Date().toISOString(),
        copyStyle: copyStyle,
      },
    };

    const templateVersion = await prisma.templateVersion.create({
      data: {
        templateId: template.id,
        version: existingVersions + 1,
        content: contentWithMetadata,
        colorPalette: result.data?.colorPalette || {},
        typography: result.data?.typography || {},
        aiCopyStyle: copyStyle,
        isActive: true,
      },
    });

    // Deactivate other versions
    await prisma.templateVersion.updateMany({
      where: {
        templateId: template.id,
        id: { not: templateVersion.id },
      },
      data: { isActive: false },
    });

    return NextResponse.json({
      success: true,
      templateId: template.id,
      templateVersionId: templateVersion.id,
      tempDir,
      isGptGenerated,
    });
  } catch (error: any) {
    console.error("Error generating website:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Failed to generate website" },
      { status: 500 }
    );
  }
}

