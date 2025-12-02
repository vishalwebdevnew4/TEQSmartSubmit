import { detectContactPage } from "./src/lib/contact-page-detector";

async function testContactPage() {
  const testUrl = process.argv[2] || "https://interiordesign.xcelanceweb.com";
  
  console.log(`\n🧪 Testing contact page detection with Playwright for: ${testUrl}\n`);
  console.log("⏱️  Starting test at:", new Date().toISOString());
  const startTime = Date.now();
  
  try {
    const result = await detectContactPage(testUrl);
    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);
    
    console.log("\n✅ Test completed!");
    console.log("⏱️  Total duration:", duration, "seconds");
    console.log("⏱️  Ended at:", new Date().toISOString());
    console.log("\n📊 Results:");
    console.log("  Status:", result.status);
    console.log("  Found:", result.found);
    console.log("  Contact URL:", result.contactUrl || "N/A");
    console.log("  Has Form:", result.hasForm);
    console.log("  Message:", result.message);
    
    // Expected duration should be at least 10+ seconds if sleep is working
    const expectedMinDuration = 10;
    if (parseFloat(duration) < expectedMinDuration) {
      console.log(`\n⚠️  WARNING: Duration (${duration}s) is less than expected minimum (${expectedMinDuration}s)`);
      console.log("   Sleep might not be applying correctly!");
    } else {
      console.log(`\n✅ Duration (${duration}s) looks good - sleep appears to be working`);
    }
    
  } catch (error: any) {
    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);
    console.error("\n❌ Test failed!");
    console.error("⏱️  Duration before error:", duration, "seconds");
    console.error("Error:", error.message);
    process.exit(1);
  }
}

testContactPage();

