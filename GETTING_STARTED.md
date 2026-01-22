# Getting Started with SudoMode

This guide will help you get SudoMode up and running in minutes.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11 or 3.12** installed
- **Node.js 18+** installed (for the dashboard)
- **pip** and **npm** package managers
- A terminal/command prompt

## Step-by-Step Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/sudomode-ai.git
cd sudomode-ai
```

### Step 2: Set Up the Backend Server

1. **Navigate to the server directory:**
   ```bash
   cd server
   ```

2. **Create a Python virtual environment:**
   ```bash
   python3.11 -m venv venv
   ```
   
   **Activate it:**
   - On macOS/Linux: `source venv/bin/activate`
   - On Windows: `venv\Scripts\activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables (optional):**
   ```bash
   # Create .env file for Slack notifications
   echo "SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL" > .env
   ```
   
   > **Note:** Slack integration is optional. You can skip this if you don't have a Slack webhook URL yet.

5. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   
   You should see:
   ```
   INFO:     Uvicorn running on http://127.0.0.1:8000
   ```

6. **Verify it's working:**
   Open http://localhost:8000/health in your browser. You should see:
   ```json
   {"status": "healthy"}
   ```

### Step 3: Set Up the Dashboard (Optional)

1. **Open a new terminal** and navigate to the dashboard:
   ```bash
   cd dashboard
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   You should see:
   ```
   VITE v7.x.x  ready in xxx ms
   ➜  Local:   http://localhost:5173/
   ```

4. **Open the dashboard:**
   Navigate to http://localhost:5173 in your browser.

### Step 4: Install the SDK

1. **Open another terminal** and navigate to the SDK:
   ```bash
   cd sdk
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test the installation:**
   ```bash
   python -c "from sudomode import SudoClient; print('SDK installed successfully!')"
   ```

## Running Your First Example

Now that everything is set up, let's run the demo:

1. **Make sure the server is running** (from Step 2)

2. **Run the demo agent:**
   ```bash
   cd sdk
   python examples/demo_agent.py
   ```

3. **Watch what happens:**
   - ✅ Read operations will be allowed
   - ⛔ Delete operations will be blocked
   - ⏳ High-value charges will pause for approval

4. **Check the dashboard:**
   - Open http://localhost:5173
   - You should see the pending approval request appear automatically
   - Click "AUTHORIZE" or "BLOCK" to approve or reject it

## Understanding the Flow

Here's what happens when you run the demo:

```
1. Agent calls: client.execute("stripe.charge", "charge", {"amount": 5000})
                    ↓
2. SDK sends request to SudoMode server
                    ↓
3. Policy Engine evaluates the request
                    ↓
4. Policy matches: "require_approval_high_amount_charge"
                    ↓
5. Server stores request and returns: REQUIRE_APPROVAL + request_id
                    ↓
6. SDK polls server every 2 seconds waiting for approval
                    ↓
7. Human reviews in dashboard and clicks "AUTHORIZE"
                    ↓
8. Server updates request status to "APPROVED"
                    ↓
9. SDK detects approval and returns True
                    ↓
10. Agent proceeds with the action
```

## Next Steps

### Customize Policies

Edit `server/policies.yaml` to define your own rules:

```yaml
rules:
  - name: "my_custom_rule"
    resource: "my_resource"
    action: "my_action"
    condition: "args.amount > 100"
    decision: "REQUIRE_APPROVAL"
    reason: "Custom reason"
```

Restart the server after making changes.

### Integrate into Your Agent

See `sdk/examples/bank_agent.py` for a more realistic integration example.

### Set Up Slack Notifications

1. Create a Slack app at https://api.slack.com/apps
2. Enable "Incoming Webhooks"
3. Add webhook to your workspace
4. Copy the webhook URL to `server/.env`

## Troubleshooting

### "Failed to fetch" error in dashboard

- Make sure the backend server is running on port 8000
- Check that CORS is enabled (it should be by default)
- Try refreshing the browser

### "Connection refused" errors

- Verify the server is running: `curl http://localhost:8000/health`
- Check that no other service is using port 8000
- Make sure you're using the correct URL in your client

### Python version issues

- Use Python 3.11 or 3.12 (not 3.14)
- Create a fresh virtual environment
- Reinstall dependencies

### Policy not matching

- Check the policy YAML syntax
- Verify resource and action names match exactly
- Review condition expressions
- Check the order of rules (first match wins)

## Need Help?

- Check the [main README](README.md) for more details
- Review the [API documentation](http://localhost:8000/docs) when server is running
- Open an issue on GitHub

---

**Happy coding! 🚀**

