const { PrismaClient } = require("@prisma/client");

const prisma = new PrismaClient();

const DOMAIN_URL = "https://interiordesign.xcelanceweb.com/";
const TEMPLATE_NAME = "Interior Design Contact Form";

async function main() {
  const domain = await prisma.domain.upsert({
    where: { url: DOMAIN_URL },
    update: {},
    create: {
      url: DOMAIN_URL,
      category: "interior-design",
      isActive: true,
    },
  });

  const fieldMappings = {
    description: "Seeded template for testing the Housefolio contact form workflow.",
    use_local_captcha_solver: true, // Enable local CAPTCHA solver by default
    pre_actions: [
      {
        type: "click",
        selector: "button:has-text(\"Alles accepteren\")",
        timeout_ms: 15000,
      },
      {
        type: "wait_for_selector",
        selector: "form button[type='submit']:has-text(\"Bericht verzenden\")",
        timeout_ms: 15000,
      },
    ],
    fields: [
      {
        selector: "input[name='name']",
        testValue: "TEQ QA User",
        note: "Primary contact name field.",
      },
      {
        selector: "input[name='email']",
        testValue: "qa@example.com",
      },
      {
        selector: "input[name='phone']",
        testValue: "555-123-4567",
        optional: true,
      },
      {
        selector: "textarea[name='comment']",
        testValue: "Automated submission from TEQSmartSubmit test seed.",
      },
    ],
    submit_selector: "button[type='submit']:has-text(\"Bericht verzenden\")",
    wait_until: "load",
    post_submit_wait_ms: 15000,
    success_message: "Submission completed",
    success_indicators: ["bedankt", "thank", "success", "verzonden", "uw bericht"],
  };

  await prisma.template.upsert({
    where: { name: TEMPLATE_NAME },
    update: {
      domainId: domain.id,
      fieldMappings,
    },
    create: {
      name: TEMPLATE_NAME,
      description: "Default automation template for Housefolio contact form.",
      fieldMappings,
      domainId: domain.id,
    },
  });

  console.log("Seeded domain and template for:", DOMAIN_URL);
}

main()
  .catch((error) => {
    console.error("Seeding failed:", error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });


