/**
 * Script to check a single domain for contact page
 */

import { PrismaClient } from '@prisma/client';
import { detectContactPage } from '../src/lib/contact-page-detector';

const prisma = new PrismaClient();

const domainUrl = process.argv[2] || 'https://www.waytopost.com';

async function checkSingleDomain() {
  try {
    console.log(`Checking domain: ${domainUrl}\n`);

    // Find domain in database
    const domain = await prisma.domain.findFirst({
      where: {
        url: domainUrl,
      },
      select: {
        id: true,
        url: true,
        contactCheckStatus: true,
        contactPageUrl: true,
      },
    });

    if (!domain) {
      console.log(`⚠️  Domain not found in database: ${domainUrl}`);
      console.log(`Running contact page detection anyway...\n`);
    } else {
      console.log(`Found in database:`);
      console.log(`  Current status: ${domain.contactCheckStatus}`);
      console.log(`  Contact page URL: ${domain.contactPageUrl || 'None'}\n`);
    }

    console.log(`Running contact page detection...\n`);
    const checkResult = await detectContactPage(domainUrl);

    console.log(`\n${'='.repeat(60)}`);
    console.log('DETECTION RESULTS');
    console.log('='.repeat(60));
    console.log(`Status: ${checkResult.status}`);
    console.log(`Found: ${checkResult.found}`);
    console.log(`Contact URL: ${checkResult.contactUrl || 'None'}`);
    console.log(`Has Form: ${checkResult.hasForm}`);
    console.log(`Message: ${checkResult.message}`);
    console.log('='.repeat(60));

    // Update domain in database if it exists
    if (domain) {
      await prisma.domain.update({
        where: { id: domain.id },
        data: {
          contactPageUrl: checkResult.contactUrl,
          contactCheckStatus: checkResult.status,
          contactCheckedAt: new Date(),
        },
      });

      // Log the check
      await prisma.contactCheck.create({
        data: {
          domainId: domain.id,
          status: checkResult.status,
          contactUrl: checkResult.contactUrl,
          message: checkResult.message,
        },
      });

      console.log(`\n✅ Database updated successfully!`);
    } else {
      console.log(`\n⚠️  Domain not in database - results not saved.`);
    }

  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

// Run the script
checkSingleDomain()
  .then(() => {
    console.log('\nCheck completed!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('Script failed:', error);
    process.exit(1);
  });

