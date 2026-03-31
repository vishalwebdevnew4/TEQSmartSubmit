/**
 * Script to re-check specific domains with error status
 */

import { PrismaClient } from '@prisma/client';
import { detectContactPage } from '../src/lib/contact-page-detector';

const prisma = new PrismaClient();

const domainsToCheck = [
  'https://www.yahoo.com',
  'https://www.xpressarticles.com',
  'https://www.wutsi.com',
  'https://www.wsumed.com',
];

async function recheckSpecificDomains() {
  try {
    console.log(`Re-checking ${domainsToCheck.length} specific domains...\n`);

    let successCount = 0;
    let stillErrorCount = 0;
    let foundCount = 0;
    let notFoundCount = 0;
    let noFormCount = 0;

    for (const domainUrl of domainsToCheck) {
      try {
        // Find domain in database
        const domain = await prisma.domain.findFirst({
          where: {
            url: domainUrl,
          },
          select: {
            id: true,
            url: true,
            contactCheckStatus: true,
          },
        });

        if (!domain) {
          console.log(`⚠️  Domain not found in database: ${domainUrl}`);
          continue;
        }

        console.log(`\nChecking: ${domain.url} (Current status: ${domain.contactCheckStatus})`);
        
        const checkResult = await detectContactPage(domain.url);

        // Update domain in database
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

        // Update counters and log result
        if (checkResult.status === 'found') {
          foundCount++;
          successCount++;
          console.log(`  ✅ Found: ${checkResult.contactUrl}`);
        } else if (checkResult.status === 'not_found') {
          notFoundCount++;
          console.log(`  ⚠️  Not found: ${checkResult.message}`);
        } else if (checkResult.status === 'no_form') {
          noFormCount++;
          console.log(`  ⚠️  No form: ${checkResult.message}`);
        } else if (checkResult.status === 'error') {
          stillErrorCount++;
          console.log(`  ❌ Still error: ${checkResult.message}`);
        }

        // Delay between checks
        await new Promise(resolve => setTimeout(resolve, 2000));
      } catch (error: any) {
        stillErrorCount++;
        console.error(`  ❌ Error checking ${domainUrl}: ${error.message}`);
        
        // Try to update domain with error status
        try {
          const domain = await prisma.domain.findFirst({
            where: { url: domainUrl },
            select: { id: true },
          });
          
          if (domain) {
            await prisma.domain.update({
              where: { id: domain.id },
              data: {
                contactCheckStatus: 'error',
                contactCheckedAt: new Date(),
              },
            });

            await prisma.contactCheck.create({
              data: {
                domainId: domain.id,
                status: 'error',
                contactUrl: null,
                message: error.message || 'Unknown error during contact page check',
              },
            });
          }
        } catch (dbError) {
          console.error(`  Failed to update error status: ${dbError}`);
        }
      }
    }

    // Print summary
    console.log('\n' + '='.repeat(60));
    console.log('RE-CHECK SUMMARY');
    console.log('='.repeat(60));
    console.log(`Total domains checked: ${domainsToCheck.length}`);
    console.log(`✅ Found (with form): ${foundCount}`);
    console.log(`⚠️  Not found: ${notFoundCount}`);
    console.log(`⚠️  No form: ${noFormCount}`);
    console.log(`❌ Still error: ${stillErrorCount}`);
    console.log(`✅ Success rate: ${((successCount / domainsToCheck.length) * 100).toFixed(1)}%`);
    console.log('='.repeat(60));

  } catch (error) {
    console.error('Fatal error:', error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

// Run the script
recheckSpecificDomains()
  .then(() => {
    console.log('\nRe-check process completed!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('Script failed:', error);
    process.exit(1);
  });



