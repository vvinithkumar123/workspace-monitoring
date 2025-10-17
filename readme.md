# AWS Workspace Health Monitoring Solution
## Complete Configuration Guide with Sample Email Notification

**Document Created By:** Vineeth
**Solution Type:** CloudWatch Logs Insights + EventBridge + SNS

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Step-by-Step Configuration](#step-by-step-configuration)
5. [Sample Email Notification](#sample-email-notification)
6. [Troubleshooting](#troubleshooting)
7. [Monitoring & Verification](#monitoring--verification)

---

## Overview

This document provides a complete guide to build an automated AWS Workspace health monitoring solution that:
- Monitors 100+ AWS Workspaces in a single account
- Detects unhealthy Workspace statuses daily
- Generates automated email reports via SNS
- Uses CloudWatch Logs Insights for querying
- Triggers via EventBridge scheduled rules

**Cost Estimate:** ~$1.05/month

---

## Architecture

```
EventBridge Rule (Daily Schedule)
    ↓
CloudWatch Logs Insights Query
    ↓
SNS Topic
    ↓
Email Notification (Recipient)
```

**Data Flow:**
1. EventBridge triggers daily at scheduled time
2. CloudWatch Logs Insights executes query on Workspace logs
3. Query results filtered for unhealthy statuses
4. Results published to SNS Topic
5. SNS sends email to subscribed recipients

---

## Prerequisites

- AWS Account with 100 Workspaces deployed
- CloudWatch Logs enabled for Workspaces
- SNS configured for email delivery
- Appropriate IAM permissions
- Email address(es) for notifications

---

## Step-by-Step Configuration

### Step 1: Verify CloudWatch Logs for Workspace Events

**Objective:** Ensure Workspace logs are being captured in CloudWatch

**In AWS Console:**

1. Navigate to **CloudWatch** service
2. Click **Logs** in left sidebar
3. Click **Log Groups**
4. Search for log groups with patterns:
   - `/aws/workspaces/*`
   - `workspaces-logs`
   - Custom workspace event logs

**If No Logs Exist:**

1. Open **WorkSpaces Console**
2. Click **Account Settings** (or **Settings**)
3. Find **Logging** section
4. Enable **CloudWatch Logs**
5. Select or create log group destination
6. Wait 5-10 minutes for logs to appear

**Verification:**
- Click on the log group
- Check **Log streams** tab
- Should see recent events (within last hour)
- If empty, Workspaces may not be sending logs yet

---

### Step 2: Create SNS Topic for Email Delivery

**Objective:** Set up SNS topic to receive and distribute email notifications

**In AWS Console:**

1. Navigate to **SNS** (Simple Notification Service)
2. In left sidebar, click **Topics**
3. Click **Create Topic** button (top right)

**Configure Topic:**

| Field | Value |
|-------|-------|
| Type | Standard |
| Name | `workspace-health-alerts` |
| Display name | `AWS Workspace Health Report` |
| Encryption | Leave default (optional) |

4. Click **Create Topic** button
5. Wait for topic to be created

**Add Email Subscription:**

1. Click on newly created topic: `workspace-health-alerts`
2. Scroll down to **Subscriptions** section
3. Click **Create Subscription** button

**Configure Subscription:**

| Field | Value |
|-------|-------|
| Protocol | Email |
| Endpoint | your-email@company.com |
| (Optional) Add multiple emails | separate-email@company.com |

4. Click **Create Subscription** button
5. **IMPORTANT:** Check your email inbox (and spam folder)
6. Find SNS confirmation email
7. Click **Confirm subscription** link in email
8. Verify subscription shows "Confirmed" status in AWS console

**Status Check:**
- Subscription status should show "Confirmed" (not "PendingConfirmation")
- If pending, reconfirm via email link

---

### Step 3: Create IAM Role for EventBridge

**Objective:** Create service role with permissions for EventBridge to access CloudWatch Logs and SNS

**In AWS Console:**

1. Navigate to **IAM** (Identity and Access Management)
2. Click **Roles** in left sidebar
3. Click **Create Role** button (top right)

**Select Trusted Entity:**

1. **Trusted entity type:** Select **AWS Service**
2. **Use case:** Search for and select **Events**
3. Click **Next** button

**Add Permissions:**

1. Search for permissions in the search box:
   - First, search for `CloudWatchLogsFullAccess`
   - Check the checkbox
   - Then search for `AmazonSNSFullAccess`
   - Check the checkbox

2. Click **Next** button

**Name and Review:**

| Field | Value |
|-------|-------|
| Role name | `eventbridge-workspace-health-role` |
| Description | Role for EventBridge to run Workspace health checks |

3. Click **Create Role** button

**Verify Role Created:**
- Role appears in roles list
- Has both CloudWatchLogs and SNS permissions
- Trust relationship shows service as "events.amazonaws.com"

**Optional - Create Restrictive Policy:**

If you want to limit permissions (recommended for production):

1. Click on the created role
2. Click **Add inline policy**
3. Click **JSON** tab
4. Paste this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:StartQuery",
        "logs:GetQueryResults",
        "logs:StopQuery"
      ],
      "Resource": "arn:aws:logs:*:ACCOUNT-ID:log-group:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:REGION:ACCOUNT-ID:workspace-health-alerts"
    }
  ]
}
```

5. Replace `ACCOUNT-ID` with your AWS Account ID
6. Replace `REGION` with your region (e.g., us-east-1)
7. Click **Review policy** → **Create policy**

---

### Step 4: Create CloudWatch Logs Insights Query

**Objective:** Build query to filter unhealthy Workspaces from logs

**In AWS Console:**

1. Navigate to **CloudWatch** service
2. Click **Logs** in left sidebar
3. Click **Log Groups**
4. Click on your Workspace log group (identified in Step 1)
5. Click **Logs Insights** tab (in main panel or top right)

**Enter Query:**

Copy and paste this query into the query editor:

```
fields @timestamp, workspaceId, state, userId, connectionState
| filter state like /UNHEALTHY|ERROR|STOPPED|SUSPENDED/ or connectionState = "DISCONNECTED"
| stats count() as UnhealthyCount by state, workspaceId, userId
| sort @timestamp desc
```

**Alternative Queries:**

If above query doesn't match your log structure, try:

**Option A - Simplified:**
```
fields @timestamp, workspace_id, workspace_state, user_id
| filter workspace_state in ["UNHEALTHY", "ERROR", "STOPPED"]
| stats count() as total_unhealthy
```

**Option B - Connection Issues Only:**
```
fields @timestamp, workspaceId, connectionState, userId
| filter connectionState = "DISCONNECTED" or connectionState = "UNKNOWN"
| sort @timestamp desc
```

**Option C - All Failures:**
```
fields @timestamp, workspaceId, state, errorMessage, userId
| filter ispresent(errorMessage) or state like /FAILED|ERROR|UNHEALTHY/
```

**Test Query:**

1. Click **Run query** button
2. Review results in **Results** section
3. If results appear:
   - Query is working ✓
   - Note the query structure for later use
4. If no results:
   - Check log group name is correct
   - Verify logs contain Workspace events
   - Try alternative query from above

**Select Best Query:**
- Choose the query that returns relevant unhealthy workspace data
- Note the query text exactly as you'll need it in Step 5

---

### Step 5: Create EventBridge Rule

**Objective:** Set up scheduled rule to trigger daily health check

**In AWS Console:**

1. Navigate to **EventBridge** service
2. Click **Rules** in left sidebar
3. Click **Create Rule** button (top right)

**Configure Rule Details:**

| Field | Value |
|-------|-------|
| Name | `workspace-daily-health-check` |
| Description | Daily AWS Workspace health status report |
| Event bus | default |
| Rule state | Enabled |

4. Click **Next** button

**Define Pattern:**

1. **Rule type:** Select **Schedule**
2. **Schedule pattern:** Select **Cron expression**
3. **Cron expression:** Enter one of these options:

   **Option A - Daily at 8 AM UTC:**
   ```
   0 8 * * ? *
   ```

   **Option B - Daily at Midnight UTC:**
   ```
   0 0 * * ? *
   ```

   **Option C - Daily at 6 PM UTC:**
   ```
   0 18 * * ? *
   ```

   **Option D - Business days only (Mon-Fri) at 8 AM UTC:**
   ```
   0 8 ? * MON-FRI *
   ```

   **Note:** Times are in UTC. Convert to your timezone:
   - UTC 0 = UTC
   - UTC 8 = UTC+8 (Singapore)
   - UTC -5 = EST (Eastern Standard Time)

4. Click **Next** button

**Select Target:**

1. **Target 1 - CloudWatch Logs Insights:**
   - **Target type:** CloudWatch Logs Group
   - **Log group:** Select your Workspace log group (from Step 1)
   
2. Click **Add another target**

3. **Target 2 - SNS Topic:**
   - **Target type:** SNS Topic
   - **Topic:** Select `workspace-health-alerts`
   - **Message format:** Raw

4. Configure Input Transformation (Optional - see Step 6)

5. Click **Next** button

**Review Rule:**

1. Verify all settings are correct
2. Check IAM role is assigned
3. Click **Create rule** button

**Verification:**
- Rule appears in Rules list
- Status shows "Enabled"
- Targets show "CloudWatch Logs Group" and "SNS Topic"

---

### Step 6: Transform CloudWatch Output to SNS Message (Optional)

**Objective:** Format query results into readable email

**In AWS Console:**

1. Navigate to **EventBridge** → **Rules**
2. Click your rule: `workspace-daily-health-check`
3. Click **Edit** button (top right)
4. Scroll to **Targets** section
5. Click on the **CloudWatch Logs Group** target
6. Expand **Additional settings**

**Configure Input Transformer:**

1. Find **Transform input** section
2. Check **Transform input**
3. Click **Configure input transformer**

**Input Path** (Maps data):
```json
{
  "queryResults": "$.queryResults",
  "date": "$.time"
}
```

4. Click in **Input template** field
5. Paste this template:

```
"AWS Workspace Daily Health Report - <date>

QUERY RESULTS:
<queryResults>

Dashboard Access:
https://console.aws.amazon.com/workspaces/

CloudWatch Logs:
https://console.aws.amazon.com/logs/

Generated at: <date>
"
```

6. Click **Update** button

**Alternative Template (HTML Format):**

If SNS supports HTML (some email clients):

```
"<h2>AWS Workspace Daily Health Report</h2>
<p><strong>Report Date:</strong> <date></p>
<hr/>
<h3>Unhealthy Workspaces</h3>
<pre><queryResults></pre>
<hr/>
<p><a href='https://console.aws.amazon.com/workspaces/'>AWS WorkSpaces Console</a></p>
"
```

---

### Step 7: Test the Configuration

**Objective:** Verify entire workflow functions correctly

**Manual Test - Send Custom Event:**

1. Navigate to **EventBridge** → **Rules**
2. Click your rule: `workspace-daily-health-check`
3. Click **Send events** button (top right)
4. Click **Create event**

**Fill in Test Event:**

```json
{
  "version": "0",
  "id": "test-workspace-health-check",
  "detail-type": "Scheduled Event",
  "source": "aws.events",
  "account": "123456789012",
  "time": "2025-10-17T04:06:09Z",
  "region": "us-east-1",
  "resources": [],
  "detail": {}
}
```

5. Click **Create event** button
6. **Check your email inbox** (and spam folder)
7. Verify SNS notification received within 2-3 minutes

**What to Check:**

- [ ] Email received from "AWS Notifications"
- [ ] Subject includes workspace health report
- [ ] Body contains CloudWatch query results
- [ ] Dashboard links are clickable
- [ ] No error messages in email

**If Email Not Received:**

1. Verify SNS subscription is confirmed
2. Check SNS topic in AWS console
3. Check CloudWatch Logs for errors:
   - Go to **CloudWatch** → **Log Groups**
   - Look for `/aws/events/` group
   - Review recent log entries for errors
4. Verify IAM role has correct permissions
5. Re-run test after verification

**Automatic Test - Wait for Scheduled Trigger:**

1. Note the cron schedule you set (e.g., 8 AM UTC)
2. Wait until scheduled time
3. Check email for automated report
4. Verify report contains real Workspace data

---

### Step 8: Monitor and Verify Ongoing Execution

**Objective:** Track rule execution and troubleshoot issues

**Check EventBridge Metrics:**

1. Navigate to **EventBridge** → **Rules**
2. Click your rule: `workspace-daily-health-check`
3. Click **Metrics** tab

**View Statistics:**

| Metric | Meaning |
|--------|---------|
| Invocations | Number of times rule triggered |
| Failed invocations | Number of failed executions |
| Throttled rules | Times execution was throttled |
| Target errors | Errors in publishing to SNS/CloudWatch |

4. Set time range: **Last 7 days** or **Last 30 days**
5. Look for patterns of success/failure

**Check SNS Topic Metrics:**

1. Navigate to **SNS** → **Topics**
2. Click `workspace-health-alerts` topic
3. Click **Monitoring** tab

**View SNS Statistics:**

| Metric | Meaning |
|--------|---------|
| Messages published | Total notifications sent |
| Delivery status | Success/Failure counts |
| HTTP failures | Failed email deliveries |

**Check CloudWatch Logs:**

1. Navigate to **CloudWatch** → **Log Groups**
2. Look for `/aws/events/` log group
3. Click on it
4. Review recent log entries
5. Check for error messages or warnings

**Typical Healthy Log Entry:**
```
[EventBridge] Rule: workspace-daily-health-check
Target: workspace-health-alerts (SNS)
Status: SUCCESS
Time: 2025-10-17 08:00:00 UTC
```

**Common Error Log Entries:**
```
[Error] CloudWatch Logs query failed: Log group not found
[Error] SNS publish failed: InvalidParameter - Invalid topic ARN
[Error] Access Denied: IAM role missing permissions
```

---

### Step 9: Set Up Alerts for Failed Executions (Optional)

**Objective:** Get notified if health check fails

**Create CloudWatch Alarm:**

1. Navigate to **CloudWatch** → **Alarms**
2. Click **Create alarm** button
3. **Metric:** Select EventBridge rule
4. **Statistic:** Failed invocations > 0
5. **Action:** Send SNS notification to same topic
6. Click **Create alarm**

---

## Sample Email Notification

Below is a sample of the email you'll receive from the daily health check:

---

### Email Header

**From:** AWS Notifications <no-reply@sns.amazonaws.com>

**To:** your-email@company.com

**Subject:** AWS Notification - Message

**Date:** 2025-10-17 08:00:00 UTC

---

### Email Body

```
AWS Workspace Daily Health Report - 2025-10-17 08:00:00 UTC

================================================================================

SUMMARY
────────────────────────────────────────────────────────────────────────────
Total Workspaces Monitored:          100
Unhealthy Workspaces Found:          7
Healthy Workspaces:                  93
Report Generated:                    2025-10-17 08:00:00 UTC

================================================================================

BREAKDOWN BY STATUS
────────────────────────────────────────────────────────────────────────────

UNHEALTHY (3 Workspaces)
├─ Workspace ID: ws-a1b2c3d4e5f6g7h8i
│  ├─ User: john.smith@company.com
│  ├─ Last Modified: 2025-10-16 14:32:00
│  └─ Connection State: DISCONNECTED

├─ Workspace ID: ws-x9y8z7w6v5u4t3s2r
│  ├─ User: sarah.jones@company.com
│  ├─ Last Modified: 2025-10-16 18:45:00
│  └─ Connection State: DISCONNECTED

└─ Workspace ID: ws-m1n2o3p4q5r6s7t8u
   ├─ User: mike.wilson@company.com
   ├─ Last Modified: 2025-10-16 22:15:00
   └─ Connection State: DISCONNECTED


ERROR (2 Workspaces)
├─ Workspace ID: ws-a5b4c3d2e1f0g9h8i
│  ├─ User: emma.davis@company.com
│  ├─ Last Modified: 2025-10-16 09:20:00
│  └─ Error: PCoIP Agent registration failed

└─ Workspace ID: ws-l8k7j6i5h4g3f2e1d
   ├─ User: robert.brown@company.com
   ├─ Last Modified: 2025-10-15 16:50:00
   └─ Error: Insufficient disk space


STOPPED (2 Workspaces)
├─ Workspace ID: ws-p1q2r3s4t5u6v7w8x
│  ├─ User: lisa.anderson@company.com
│  ├─ Last Modified: 2025-10-17 02:00:00
│  └─ Reason: Manual stop by administrator

└─ Workspace ID: ws-c9d8e7f6g5h4i3j2k
   ├─ User: james.taylor@company.com
   ├─ Last Modified: 2025-10-16 20:30:00
   └─ Reason: Scheduled maintenance

================================================================================

RECOMMENDED ACTIONS
────────────────────────────────────────────────────────────────────────────

FOR UNHEALTHY WORKSPACES:
  1. Check network connectivity for affected users
  2. Verify PCoIP Agent is running on Workspace
  3. Restart Workspace if necessary:
     - Right-click Workspace in console → Reboot
  4. Monitor for recovery in next report
  5. Check CloudWatch Logs for detailed diagnostics

FOR ERROR WORKSPACES:
  1. Investigate specific error messages above
  2. Check system resources (disk, memory, CPU):
     - Connect to Workspace desktop
     - Open Task Manager (Windows) or Activity Monitor (Mac)
  3. For PCoIP Agent errors:
     - Reinstall PCoIP Agent
     - Check agent logs in Event Viewer (Windows)
  4. For disk space issues:
     - Clean up temporary files
     - Contact IT for storage expansion
  5. Consult AWS documentation or contact AWS Support

FOR STOPPED WORKSPACES:
  1. Verify if status is intentional (maintenance/testing)
  2. If unintended, restart immediately:
     - Click Workspace → Start in console
  3. Notify affected users of status
  4. Monitor for startup completion
  5. Update change log if scheduled maintenance

================================================================================

QUICK LINKS
────────────────────────────────────────────────────────────────────────────

AWS WorkSpaces Console:
https://console.aws.amazon.com/workspaces/

WorkSpaces Dashboard (US East 1):
https://console.aws.amazon.com/workspaces/?region=us-east-1

CloudWatch Logs - Workspace Events:
https://console.aws.amazon.com/logs/home?region=us-east-1

AWS WorkSpaces Troubleshooting Guide:
https://docs.aws.amazon.com/workspaces/latest/userguide/

EventBridge Rules Status:
https://console.aws.amazon.com/events/home?region=us-east-1#/rules

================================================================================

DETAILED QUERY RESULTS
────────────────────────────────────────────────────────────────────────────

@timestamp                | workspaceId              | state        | userId
──────────────────────────┼──────────────────────────┼──────────────┼──────────────────────────
2025-10-16T14:32:00.000Z  | ws-a1b2c3d4e5f6g7h8i    | UNHEALTHY    | john.smith@company.com
2025-10-16T18:45:00.000Z  | ws-x9y8z7w6v5u4t3s2r    | UNHEALTHY    | sarah.jones@company.com
2025-10-16T22:15:00.000Z  | ws-m1n2o3p4q5r6s7t8u    | UNHEALTHY    | mike.wilson@company.com
2025-10-16T09:20:00.000Z  | ws-a5b4c3d2e1f0g9h8i    | ERROR        | emma.davis@company.com
2025-10-15T16:50:00.000Z  | ws-l8k7j6i5h4g3f2e1d    | ERROR        | robert.brown@company.com
2025-10-17T02:00:00.000Z  | ws-p1q2r3s4t5u6v7w8x    | STOPPED      | lisa.anderson@company.com
2025-10-16T20:30:00.000Z  | ws-c9d8e7f6g5h4i3j2k    | STOPPED      | james.taylor@company.com

================================================================================

REPORT METADATA
────────────────────────────────────────────────────────────────────────────
Report Type:             Daily Automated Health Check
Account ID:              123456789012
Region:                  us-east-1
Report Generated By:     AWS CloudWatch Logs Insights + EventBridge
Generated At:            2025-10-17 08:00:09 UTC
Next Report:             2025-10-18 08:00:00 UTC (24 hours)

For support or to modify this report, contact your AWS administrator.

================================================================================
```

---

### Alternative - Simplified Email Format

If you prefer a more concise format, the email could also look like:

```
AWS Workspace Health Alert - Daily Report
Date: 2025-10-17

⚠️ ALERT: 7 Unhealthy Workspaces Detected

UNHEALTHY (3):
  • ws-a1b2c3d4e5f6g7h8i | john.smith@company.com | DISCONNECTED
  • ws-x9y8z7w6v5u4t3s2r | sarah.jones@company.com | DISCONNECTED
  • ws-m1n2o3p4q5r6s7t8u | mike.wilson@company.com | DISCONNECTED

ERROR (2):
  • ws-a5b4c3d2e1f0g9h8i | emma.davis@company.com | PCoIP Agent failed
  • ws-l8k7j6i5h4g3f2e1d | robert.brown@company.com | Disk space low

STOPPED (2):
  • ws-p1q2r3s4t5u6v7w8x | lisa.anderson@company.com | Manual stop
  • ws-c9d8e7f6g5h4i3j2k | james.taylor@company.com | Maintenance

📊 Summary:
✓ Total: 100 | ✓ Healthy: 93 | ⚠️ Unhealthy: 7

📋 Dashboard: https://console.aws.amazon.com/workspaces/

---
```

---

## Troubleshooting

### Issue 1: No Emails Received

**Symptoms:**
- SNS topic created but no email arrives
- Test event sent but nothing received

**Solutions:**

| Step | Action |
|------|--------|
| 1 | Check **email spam/junk folder** for SNS confirmation |
| 2 | Verify SNS subscription status is **"Confirmed"** (not "PendingConfirmation") |
| 3 | Go to SNS console → Topic → Subscriptions → verify endpoint |
| 4 | Check SNS Metrics for "Messages Published" count |
| 5 | Verify email address is spelled correctly |
| 6 | Try subscribing different email address as test |
| 7 | Check AWS Service Health dashboard for SNS issues |

**If Still Not Working:**
1. Delete and recreate SNS topic
2. Resubscribe email address
3. Confirm subscription again
4. Run test event

---

### Issue 2: EventBridge Rule Not Triggering

**Symptoms:**
- Rule shows in console but never executes
- Scheduled time passes with no email
- Invocation count remains 0

**Solutions:**

| Step | Action |
|------|--------|
| 1 | Verify rule status is **"Enabled"** (not Disabled) |
| 2 | Check cron expression syntax is valid |
| 3 | Verify current time hasn't passed scheduled time |
| 4 | Convert UTC time to your local timezone |
| 5 | Check EventBridge Metrics for Invocations count |
| 6 | Run manual test event to verify rule works |

**Verify Cron Expression:**
- Use AWS Cron Expression Helper
- Test expression: `0 8 * * ? *` (daily at 8 AM UTC)
- Make sure no typos in expression

---

### Issue 3: Empty or No Query Results

**Symptoms:**
- CloudWatch query returns no results
- Email contains "No data found"
- Query runs but shows 0 records

**Solutions:**

| Step | Action |
|------|--------|
| 1 | Verify log group contains Workspace events |
| 2 | Check log group has recent data (within 24 hours) |
| 3 | Confirm Workspace logging is **enabled** |
| 4 | Try different CloudWatch query (use alternatives from Step 4) |
| 5 | Verify field names match your log structure |
| 6 | Check if Workspaces are actually unhealthy |
| 7 | Review log data structure in log group |

**Manual Log Verification:**
1. Go to **CloudWatch** → **Log Groups**
2. Click log group
3. Click **Log Streams**
4. Open latest stream
5. Check raw log entries
6. Compare field names to your query

---

### Issue 4: IAM Permission Errors

**Symptoms:**
- EventBridge rule fails to execute
- CloudWatch logs show "Access Denied"
- SNS publish fails with "Unauthorized"

**Solutions:**

| Step | Action |
|------|--------|
| 1 | Verify IAM role is assigned to EventBridge rule |
| 2 | Check role has `CloudWatchLogsFullAccess` permission |
| 3 | Check role has `AmazonSNSFullAccess` permission |
| 4 | Verify role trust relationship includes `events.amazonaws.com` |
| 5 | Check resource ARNs in policies are correct |
| 6 | Verify account ID in ARNs matches your account |

**Check IAM Role:**
1. Go to **IAM** → **Roles**
2. Click role: `eventbridge-workspace-health-role`
3. Check **Permissions** tab for required policies
4. Click **Trust relationships** tab
5. Verify `events.amazonaws.com` is listed

---

### Issue 5: Workspace Logs Not Available

**Symptoms:**
- Log group doesn't exist
- Log group exists but is empty
- "Log group not found" errors

**Solutions:**

| Step | Action |
|------|--------|
| 1 | Enable Workspace logging in WorkSpaces settings |
| 2 | Select CloudWatch Logs as log destination |
| 3 | Create or select log group name |
| 4 | Wait 10-15 minutes for first logs to appear |
| 5 | Check log group region matches Workspace region |
| 6 | Verify IAM permissions for Workspace service |

**Enable Workspace Logging:**
1. Go to **WorkSpaces Console**
2. Click **Settings** (or **Account Settings**)
3. Find **Workspace Status** or **Logging** section
4. Enable **CloudWatch Logs**
5. Select existing log group or create new one
6. Name format: `/aws/workspaces/` or similar
7. Click **Update**
8. Wait for logs to start flowing

---

### Issue 6: Malformed Query Results in Email

**Symptoms:**
- Email contains raw JSON or unformatted data
- Query results are unreadable
- Email template not applied correctly

**Solutions:**

| Step | Action |
|------|--------|
| 1 | Check Input Transformer is configured correctly |
| 2 | Verify JSON syntax in Input Path is valid |
| 3 | Check Input Template has correct placeholder variables |
| 4 | Verify CloudWatch query returns valid JSON |
| 5 | Test with simpler template first |

**Fix Input Template:**
1. Go to **EventBridge** → **Rules** → Your rule
2. Click **Edit**
3. Scroll to Target section
4. Click CloudWatch target
5. Expand **Additional settings**
6. Check **Input transformer** settings
7. Verify placeholders match actual data
8. Click **Update**

---

## Monitoring & Verification

### Daily Monitoring Checklist

| Item | Frequency | Action |
|------|-----------|--------|
| Email Receipt | Daily | Check for report email at scheduled time |
| Inbox Folder | Daily | Verify email in main inbox (not spam) |
| Report Content | Daily | Review unhealthy workspace count/details |
| Action Items | Daily | Note any workspaces needing attention |

### Weekly Verification

**Each Week:**

1. Go to **EventBridge** → **Rules** → Your rule
2. Check **Metrics** tab
3. Review:
   - Total invocations (should be 7 for weekly)
   - Failed invocations (should be 0)
   - Throttled rules (should be 0)

4. Go to **SNS** → Topics → Your topic
5. Check **Monitoring** tab
6. Review:
   - Messages published (should match invocations)
   - Delivery status (should be all successful)

### Monthly Reporting

**Each Month:**

1. **Review trends:**
   - Peak times for unhealthy workspaces
   - Most common failure states
   - Users with recurring issues

2. **Identify patterns:**
   - Specific workspace IDs consistently failing
   - Time-of-day correlation with failures
   - User or department patterns

3. **Take action:**
   - Replace consistently failing workspaces
   - Address systemic issues
   - Update configuration if needed

### Performance Metrics Target

| Metric | Target | Notes |
|--------|--------|-------|
| Rule Success Rate | 99%+ | Should rarely fail |
| Email Delivery | 100% | All emails should arrive |
| Query Execution | < 5 sec | CloudWatch query should run quickly |
| End-to-End Time | < 2 min | From trigger to email in inbox |

---

## Summary of Configuration

### Resources Created

| Resource | Name | Type | Purpose |
|----------|------|------|---------|
| SNS Topic | workspace-health-alerts | SNS | Email distribution |
| EventBridge Rule | workspace-daily-health-check | EventBridge | Daily scheduler |
| IAM Role | eventbridge-workspace-health-role | IAM | Service permissions |

### Key Settings

| Component | Setting | Value |
|-----------|---------|-------|
| **SNS** | Topic Name | workspace-health-alerts |
| **SNS** | Protocol | Email |
| **EventBridge** | Schedule | 0 8 * * ? * (daily 8 AM UTC) |
| **EventBridge** | Target 1 | CloudWatch Logs Insights |
| **EventBridge** | Target 2 | SNS Topic |
| **IAM** | Role Name | eventbridge-workspace-health-role |
| **CloudWatch** | Query | Filter for UNHEALTHY/ERROR/STOPPED states |

### Monthly Cost Breakdown

| Service | Usage | Cost |
|---------|-------|------|
| EventBridge | 30 rules × 1 invocation/day | $0.35 |
| CloudWatch Logs Insights | 30 queries | $0.25 |
| SNS | 30 emails | $0.50 |
| **Total** | | **~$1.10/month** |

---

## Next Steps

1. ✅ Follow Steps 1-8 in order
2. ✅ Test configuration with manual event
3. ✅ Wait for first scheduled execution
4. ✅ Verify email received
5. ✅ Review sample output against your data
6. ✅ Set up ongoing monitoring
7. ✅ Create CloudWatch alarm for failures (optional)
8. ✅ Document in runbook for team

---

## Document Information

**Created By:** vvinithkumar123  
**Date:** 2025-10-17  
**Time:** 04:06:09 UTC  
**Version:** 1.0  
**Last Updated:** 2025-10-17

---

## Appendix: Quick Reference

### Cron Expression Examples

```
0 0 * * ? *     = Daily at midnight UTC
0 8 * * ? *     = Daily at 8 AM UTC
0 12 * * ? *    = Daily at noon UTC
0 18 * * ? *    = Daily at 6 PM UTC
0 8 ? * MON-FRI * = Weekdays at 8 AM UTC
0 */4 * * ? *   = Every 4 hours
0 9,17 * * ? *  = At 9 AM and 5 PM UTC
```

### AWS Service Links

- [AWS WorkSpaces Console](https://console.aws.amazon.com/workspaces/)
- [CloudWatch Logs](https://console.aws.amazon.com/logs/)
- [EventBridge Rules](https://console.aws.amazon.com/events/home#/rules)
- [SNS Topics](https://console.aws.amazon.com/sns/)
- [IAM Roles](https://console.aws.amazon.com/iam/home#/roles)

### Support Resources

- [AWS WorkSpaces Documentation](https://docs.aws.amazon.com/workspaces/)
- [AWS EventBridge Documentation](https://docs.aws.amazon.com/eventbridge/)
- [AWS SNS Documentation](https://docs.aws.amazon.com/sns/)
- [CloudWatch Logs Insights Documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html)

---

**End of Document**

---



