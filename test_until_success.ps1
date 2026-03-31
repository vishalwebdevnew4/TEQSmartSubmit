# Test API submission until success - Simple version
param(
    [int]$SubmissionId = 0
)

if ($SubmissionId -eq 0) {
    # Start new submission
    $body = @{
        url = "https://interiordesign.xcelanceweb.com/"
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

    Write-Host "Starting new submission..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000/api/run" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
        $result = $response.Content | ConvertFrom-Json
        $SubmissionId = $result.submissionId
        Write-Host "Submission ID: $SubmissionId" -ForegroundColor Green
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`nPolling for status updates (Ctrl+C to stop)..." -ForegroundColor Yellow
Write-Host ""

$startTime = Get-Date
$lastStatus = ""
$checkCount = 0

while ($true) {
    $elapsed = (Get-Date) - $startTime
    $timeStr = "{0:mm\:ss}" -f $elapsed
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000/api/logs?limit=100" -Method GET -TimeoutSec 10
        $data = $response.Content | ConvertFrom-Json
        $submission = $data.logs | Where-Object { $_.id -eq $SubmissionId } | Select-Object -First 1
        
        if ($submission) {
            $status = $submission.status
            $message = $submission.message
            
            if ($status -ne $lastStatus) {
                $color = switch ($status) {
                    "success" { "Green" }
                    "failed" { "Red" }
                    "error" { "Red" }
                    default { "Yellow" }
                }
                Write-Host "[$timeStr] Status: $status" -ForegroundColor $color
                $lastStatus = $status
                
                if ($status -eq "success") {
                    Write-Host "`nSUCCESS! Form submitted successfully!" -ForegroundColor Green
                    if ($message) {
                        Write-Host "`nMessage:" -ForegroundColor Cyan
                        Write-Host $message
                    }
                    exit 0
                } elseif ($status -eq "failed" -or $status -eq "error") {
                    Write-Host "`nFAILED! Submission did not succeed." -ForegroundColor Red
                    if ($message) {
                        Write-Host "`nError:" -ForegroundColor Red
                        Write-Host $message
                    }
                    exit 1
                }
            }
            
            # Show progress message every 10 checks
            if ($checkCount % 10 -eq 0 -and $status -eq "running") {
                $preview = if ($message -and $message.Length -gt 80) { 
                    $message.Substring(0, 80) + "..." 
                } else { 
                    $message 
                }
                if ($preview) {
                    Write-Host "   $preview" -ForegroundColor Gray
                }
            }
        } else {
            if ($checkCount -eq 0) {
                Write-Host "[$timeStr] Waiting for submission to appear..." -ForegroundColor Gray
            }
        }
        
        $checkCount++
        Start-Sleep -Seconds 2
        
    } catch {
        Write-Host "[$timeStr] Error checking status: $($_.Exception.Message)" -ForegroundColor Red
        Start-Sleep -Seconds 3
    }
}

