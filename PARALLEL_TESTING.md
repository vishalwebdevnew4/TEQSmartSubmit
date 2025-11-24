# Parallel reCAPTCHA Testing Guide

This guide explains how to use the parallel reCAPTCHA solver to fill multiple forms simultaneously.

## Overview

The parallel solver runs multiple browser instances concurrently, each:
1. Filling form fields
2. Solving reCAPTCHA with audio challenge
3. Submitting the form

This provides significant speed improvements compared to sequential processing.

## Usage

### Basic Usage (5 instances)
```bash
python3 test_recaptcha_parallel.py
```

### Custom Number of Instances
```bash
python3 test_recaptcha_parallel.py -n 10
```

### Custom URL
```bash
python3 test_recaptcha_parallel.py -u "https://your-website.com/contact"
```

### Headless Mode (faster, no visible browsers)
```bash
python3 test_recaptcha_parallel.py --headless
```

### All Options Combined
```bash
python3 test_recaptcha_parallel.py -n 10 -u "https://example.com/contact" --headless
```

## Performance

- **Sequential**: 5 forms × 60 seconds = ~300 seconds (5 minutes)
- **Parallel**: 5 forms in ~60-90 seconds = **3-5x faster**

The actual speed depends on:
- Network latency
- CAPTCHA solving time
- Server response time

## Output

The script provides:
- Real-time progress for each instance
- Summary statistics
- JSON file with detailed results
- Success/failure counts

## Example Output

```
================================================================================
🚀 PARALLEL RECAPTCHA AUDIO CHALLENGE SOLVER
================================================================================

📍 URL: https://interiordesign.xcelanceweb.com/contact
🔢 Instances: 5
🖥️  Headless: False
⚡ Running in parallel for maximum speed!

================================================================================

🚀 Launching 5 parallel instances...

[Instance 1] ⏳ Starting...
[Instance 2] ⏳ Starting...
[Instance 3] ⏳ Starting...
[Instance 4] ⏳ Starting...
[Instance 5] ⏳ Starting...
[Instance 1] ✅ Filled 4 fields
[Instance 2] ✅ Filled 4 fields
[Instance 1] 🔐 Solving CAPTCHA...
[Instance 2] 🔐 Solving CAPTCHA...
...

================================================================================
📊 RESULTS SUMMARY
================================================================================

[Instance 1] ✅ SUCCESS
   Duration: 65.23s
   Fields filled: 4
   CAPTCHA solved: Yes
   Form submitted: Yes

[Instance 2] ✅ SUCCESS
   Duration: 68.45s
   Fields filled: 4
   CAPTCHA solved: Yes
   Form submitted: Yes

...

================================================================================
📈 STATISTICS
================================================================================
✅ Successful: 5/5
❌ Failed: 0/5
⏱️  Total time: 72.34s
⚡ Average time per instance: 14.47s
🚀 Speed improvement: ~5x faster than sequential
================================================================================

💾 Results saved to: parallel_results_20241124_123456.json
```

## Configuration

### Adjusting Number of Instances

More instances = faster overall, but:
- Higher CPU/memory usage
- May hit rate limits
- Network bandwidth considerations

Recommended:
- **Headless mode**: 5-10 instances
- **Visible browsers**: 3-5 instances (limited by screen space)

### Form Field Customization

Edit the `form_data` dictionary in `fill_form_and_solve_captcha()` function:

```python
form_data = {
    'name': f'Test User {instance_id}',
    'email': f'test{instance_id}@example.com',
    'phone': f'555-{1000 + instance_id}-4567',
    'message': f'Automated test #{instance_id}',
}
```

## Troubleshooting

### All Instances Failing
- Check network connectivity
- Verify URL is accessible
- Check if site has rate limiting

### Some Instances Failing
- Normal - CAPTCHA solving can be inconsistent
- Check error messages in results JSON
- Retry failed instances

### High CPU/Memory Usage
- Reduce number of instances
- Use headless mode
- Close other applications

## Best Practices

1. **Start Small**: Test with 2-3 instances first
2. **Monitor Resources**: Watch CPU/memory usage
3. **Respect Rate Limits**: Don't overwhelm the server
4. **Use Headless**: Faster and less resource-intensive
5. **Save Results**: Always review the JSON results file

## Integration

The parallel solver can be integrated into your automation workflow:

```python
from test_recaptcha_parallel import run_parallel_submissions

# Run 5 parallel submissions
success = await run_parallel_submissions(
    num_instances=5,
    url="https://example.com/contact",
    headless=True
)
```

## Notes

- Each instance runs independently
- CAPTCHA solving happens in parallel (not sequential)
- Results are saved to JSON for analysis
- Browser instances are automatically cleaned up

