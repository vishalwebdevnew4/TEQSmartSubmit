# Test API submission until success
$body = @{
    url = "https://www.teqtop.com/contact/"
    template = @{
        fields = @()
        captcha = $true
        headless = $false
        use_auto_detect = $true
        use_local_captcha_solver = $true
        captcha_service = "local"
        submit_selector = "button[type='submit'], input[type='submit'], button:has-text('Submit'), button:has-text('Send'), button:has-text('Send message')"
        post_submit_wait_ms = 30000
        captcha_timeout_ms = 600000
        wait_until = "load"
        test_data = @{
            name = "TEQ QA User"
            email = "test@example.com"
            phone = "+1234567890"
            company = "Test Company"
            message = "This is an automated test submission from TEQSmartSubmit."
            subject = "Test Inquiry"
        }
    }
    domainId = 19
    templateId = 1
    isTest = $true
} | ConvertTo-Json -Depth 10

Write-Host "🚀 Starting submission test..." -ForegroundColor Cyan
Write-Host ""

# Submit the request
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/run" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30 -ErrorAction Stop
    $result = $response.Content | ConvertFrom-Json
    $submissionId = $result.submissionId
    
    Write-Host "✅ Submission started!" -ForegroundColor Green
    Write-Host "   Submission ID: $submissionId" -ForegroundColor Yellow
    Write-Host "   Status: $($result.status)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "⏳ Waiting for automation to complete..." -ForegroundColor Cyan
    Write-Host ""
    
    # Poll for status updates
    $maxWaitTime = 600  # 10 minutes max
    $startTime = Get-Date
    $lastStatus = ""
    $checkCount = 0
    
    while ($true) {
        $elapsed = (Get-Date) - $startTime
        if ($elapsed.TotalSeconds -gt $maxWaitTime) {
            Write-Host "⏰ Timeout: Exceeded $maxWaitTime seconds" -ForegroundColor Red
            break
        }
        
        Start-Sleep -Seconds 3  # Check every 3 seconds
        
        try {
            # Query logs API to get submission status - get more logs to find our submission
            $statusResponse = Invoke-WebRequest -Uri "http://localhost:3000/api/logs?limit=100" -Method GET -TimeoutSec 10 -ErrorAction Stop
            $logsData = $statusResponse.Content | ConvertFrom-Json
            $submission = $logsData.logs | Where-Object { $_.id -eq $submissionId } | Select-Object -First 1
            
            if (-not $submission) {
                # Submission not found yet, continue waiting
                if ($checkCount -eq 0) {
                    Write-Host "   Waiting for submission to appear..." -ForegroundColor Gray
                }
                $checkCount++
                continue
            }
            
            $currentStatus = $submission.status
            $message = $submission.message
            
            # Only print if status changed
            if ($currentStatus -ne $lastStatus) {
                $checkCount++
                $timeStr = $elapsed.ToString("mm\:ss")
                Write-Host "[$timeStr] Status: $currentStatus" -ForegroundColor $(if ($currentStatus -eq "success") { "Green" } elseif ($currentStatus -eq "failed") { "Red" } else { "Yellow" })
                
                if ($message -and $message.Length -gt 0 -and $message -ne "Automation in progress...") {
                    $preview = if ($message.Length -gt 100) { $message.Substring(0, 100) + "..." } else { $message }
                    Write-Host "   Message: $preview" -ForegroundColor Gray
                }
                
                $lastStatus = $currentStatus
            }
            
            # Check if completed
            if ($currentStatus -eq "success" -or $currentStatus -eq "submitted") {
                Write-Host ""
                if ($currentStatus -eq "success") {
                    Write-Host "✅ SUCCESS! Form submitted successfully!" -ForegroundColor Green
                } else {
                    Write-Host "✅ SUBMITTED! Form submission completed!" -ForegroundColor Green
                }
                Write-Host "   Submission ID: $submissionId" -ForegroundColor Yellow
                Write-Host "   Total time: $timeStr" -ForegroundColor Yellow
                if ($message) {
                    Write-Host ""
                    Write-Host "Final message:" -ForegroundColor Cyan
                    Write-Host $message
                }
                exit 0
            } elseif ($currentStatus -eq "failed" -or $currentStatus -eq "error") {
                Write-Host ""
                Write-Host "❌ FAILED! Submission did not succeed." -ForegroundColor Red
                Write-Host "   Submission ID: $submissionId" -ForegroundColor Yellow
                Write-Host "   Total time: $timeStr" -ForegroundColor Yellow
                if ($message) {
                    Write-Host ""
                    Write-Host "Error message:" -ForegroundColor Red
                    Write-Host $message
                }
                exit 1
            }
        } catch {
            # API might not be ready yet, continue polling
            if ($checkCount -eq 0) {
                Write-Host "   Waiting for submission to start..." -ForegroundColor Gray
            }
        }
    }
    
} catch {
    Write-Host "❌ Error submitting request:" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host $responseBody
    } else {
        Write-Host $_.Exception.Message
    }
    exit 1
}

