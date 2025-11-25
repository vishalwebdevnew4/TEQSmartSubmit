#!/bin/bash
# One-liner to deploy and test on server
# Copy this entire command to run on your server via SSH

cat << 'EOF'
# ============================================================================
# ONE-LINER COMMAND FOR SERVER TESTING
# ============================================================================
# Copy and paste this entire block into your SSH session:
# ============================================================================

cd /var/www/html/TEQSmartSubmit && \
cp automation/submission/form_discovery.py /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py && \
echo "✅ File deployed" && \
grep -q "def safe_write" /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py && \
echo "✅ Fix verified in deployed file" && \
python3 -m py_compile /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py && \
echo "✅ Syntax check passed" && \
echo "" && \
echo "🎉 Deployment complete! The fix is now active on the server." && \
echo "" && \
echo "📋 Next: Test a submission through the web interface." && \
echo "   The script should now progress past 'Function called' without hanging."

# ============================================================================
# OR use the deployment script:
# ============================================================================

# cd /var/www/html/TEQSmartSubmit && bash deploy_and_test_fix.sh

EOF

