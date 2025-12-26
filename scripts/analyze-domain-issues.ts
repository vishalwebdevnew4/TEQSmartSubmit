/**
 * Script to analyze why domains have issues
 * Provides statistics on error types and common failure patterns
 */

import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function analyzeDomainIssues() {
  try {
    console.log('Analyzing domain issues...\n');

    // Get all domains with their latest contact check
    const domains = await prisma.domain.findMany({
      select: {
        id: true,
        url: true,
        contactCheckStatus: true,
        contactPageUrl: true,
      },
    });

    // Get latest contact check messages for error analysis
    const contactChecks = await prisma.contactCheck.findMany({
      where: {
        status: { in: ['error', 'not_found'] },
      },
      orderBy: {
        checkedAt: 'desc',
      },
      select: {
        domainId: true,
        status: true,
        message: true,
        checkedAt: true,
      },
    });

    // Group by status
    const statusCounts: Record<string, number> = {};
    domains.forEach(d => {
      statusCounts[d.contactCheckStatus || 'unknown'] = (statusCounts[d.contactCheckStatus || 'unknown'] || 0) + 1;
    });

    console.log('='.repeat(70));
    console.log('DOMAIN STATUS SUMMARY');
    console.log('='.repeat(70));
    Object.entries(statusCounts).forEach(([status, count]) => {
      const percentage = ((count / domains.length) * 100).toFixed(1);
      console.log(`${status.padEnd(20)}: ${count.toString().padStart(6)} (${percentage}%)`);
    });
    console.log(`Total domains: ${domains.length}`);
    console.log('='.repeat(70));

    // Analyze error messages
    console.log('\n' + '='.repeat(70));
    console.log('ERROR MESSAGE ANALYSIS');
    console.log('='.repeat(70));

    const errorPatterns: Record<string, number> = {
      'Network/Connection': 0,
      'Timeout': 0,
      'SSL/Certificate': 0,
      'HTTP 403 (Forbidden)': 0,
      'HTTP 404 (Not Found)': 0,
      'HTTP 500 (Server Error)': 0,
      'HTTP 503 (Service Unavailable)': 0,
      'HTTP 429 (Rate Limited)': 0,
      'Connection Refused': 0,
      'DNS/ENOTFOUND': 0,
      'Page Not Accessible': 0,
      'No Contact Link': 0,
      'Other': 0,
    };

    contactChecks.forEach(check => {
      const msg = (check.message || '').toLowerCase();
      
      if (msg.includes('network error') || msg.includes('fetch failed') || msg.includes('econnreset')) {
        errorPatterns['Network/Connection']++;
      } else if (msg.includes('timeout') || msg.includes('took too long')) {
        errorPatterns['Timeout']++;
      } else if (msg.includes('ssl') || msg.includes('certificate') || msg.includes('tlsv1')) {
        errorPatterns['SSL/Certificate']++;
      } else if (msg.includes('403') || msg.includes('forbidden')) {
        errorPatterns['HTTP 403 (Forbidden)']++;
      } else if (msg.includes('404') || msg.includes('not found')) {
        errorPatterns['HTTP 404 (Not Found)']++;
      } else if (msg.includes('500') || msg.includes('internal server error')) {
        errorPatterns['HTTP 500 (Server Error)']++;
      } else if (msg.includes('503') || msg.includes('service unavailable')) {
        errorPatterns['HTTP 503 (Service Unavailable)']++;
      } else if (msg.includes('429') || msg.includes('rate limit')) {
        errorPatterns['HTTP 429 (Rate Limited)']++;
      } else if (msg.includes('connection refused') || msg.includes('econnrefused')) {
        errorPatterns['Connection Refused']++;
      } else if (msg.includes('enotfound') || msg.includes('dns') || msg.includes('getaddrinfo')) {
        errorPatterns['DNS/ENOTFOUND']++;
      } else if (msg.includes('not accessible') || msg.includes('page is not accessible')) {
        errorPatterns['Page Not Accessible']++;
      } else if (msg.includes('contact page link not found') || msg.includes('no contact link')) {
        errorPatterns['No Contact Link']++;
      } else {
        errorPatterns['Other']++;
      }
    });

    const totalErrors = contactChecks.length;
    Object.entries(errorPatterns)
      .filter(([_, count]) => count > 0)
      .sort(([_, a], [__, b]) => b - a)
      .forEach(([pattern, count]) => {
        const percentage = totalErrors > 0 ? ((count / totalErrors) * 100).toFixed(1) : '0.0';
        console.log(`${pattern.padEnd(30)}: ${count.toString().padStart(6)} (${percentage}%)`);
      });

    console.log(`\nTotal error/not_found checks analyzed: ${totalErrors}`);
    console.log('='.repeat(70));

    // Sample error messages
    console.log('\n' + '='.repeat(70));
    console.log('SAMPLE ERROR MESSAGES');
    console.log('='.repeat(70));
    
    const uniqueErrors = new Map<string, number>();
    contactChecks.slice(0, 100).forEach(check => {
      const msg = check.message || 'No message';
      uniqueErrors.set(msg, (uniqueErrors.get(msg) || 0) + 1);
    });

    Array.from(uniqueErrors.entries())
      .sort(([_, a], [__, b]) => b - a)
      .slice(0, 10)
      .forEach(([msg, count]) => {
        const truncated = msg.length > 80 ? msg.substring(0, 77) + '...' : msg;
        console.log(`[${count}x] ${truncated}`);
      });

    console.log('='.repeat(70));

    // Recommendations
    console.log('\n' + '='.repeat(70));
    console.log('RECOMMENDATIONS');
    console.log('='.repeat(70));
    
    const errorCount = statusCounts['error'] || 0;
    const notFoundCount = statusCounts['not_found'] || 0;
    const totalIssues = errorCount + notFoundCount;
    const issuePercentage = ((totalIssues / domains.length) * 100).toFixed(1);

    console.log(`\n📊 Current Status:`);
    console.log(`   - ${issuePercentage}% of domains have issues (${totalIssues}/${domains.length})`);
    console.log(`   - ${errorCount} domains with errors`);
    console.log(`   - ${notFoundCount} domains with no contact page found`);

    if (errorPatterns['Network/Connection'] > 0 || errorPatterns['Timeout'] > 0) {
      console.log(`\n🔧 Network Issues:`);
      console.log(`   - Many domains may be slow or temporarily unavailable`);
      console.log(`   - Consider increasing timeout values`);
      console.log(`   - Add more retry logic for transient failures`);
    }

    if (errorPatterns['HTTP 403 (Forbidden)'] > 0) {
      console.log(`\n🔒 Access Issues:`);
      console.log(`   - Some sites are blocking automated requests`);
      console.log(`   - Consider using different User-Agent strings`);
      console.log(`   - May need to respect robots.txt`);
    }

    if (errorPatterns['SSL/Certificate'] > 0) {
      console.log(`\n🔐 SSL Issues:`);
      console.log(`   - Some sites have certificate problems`);
      console.log(`   - HTTP fallback is already implemented`);
    }

    if (errorPatterns['Page Not Accessible'] > 0 || errorPatterns['No Contact Link'] > 0) {
      console.log(`\n🔍 Detection Issues:`);
      console.log(`   - Some sites may have contact forms in non-standard locations`);
      console.log(`   - Consider improving form detection on homepage`);
      console.log(`   - Some sites may require JavaScript rendering`);
    }

    console.log(`\n✅ Next Steps:`);
    console.log(`   1. Run recheck script for error domains: npm run recheck-errors`);
    console.log(`   2. Review and improve detection for common patterns`);
    console.log(`   3. Consider implementing a queue system for retries`);
    console.log(`   4. Add more aggressive retry logic for network errors`);

    console.log('='.repeat(70));

  } catch (error) {
    console.error('Error analyzing domains:', error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

// Run the script
analyzeDomainIssues()
  .then(() => {
    console.log('\nAnalysis completed!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('Script failed:', error);
    process.exit(1);
  });

