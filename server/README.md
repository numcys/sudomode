# SudoMode Server

## Python Version Compatibility

**Recommended: Python 3.11 or 3.12**

Python 3.14 is very new and has compatibility issues with `pydantic-core` compilation. The build process fails because Python 3.14 changed the `ForwardRef._evaluate()` API.

### Quick Fix: Use Python 3.11

If you have Python 3.11 installed (which you do), recreate your virtual environment:

```bash
# Remove old venv
rm -rf venv

# Create new venv with Python 3.11
python3.11 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Alternative: Try Latest Pydantic

If you must use Python 3.14, try installing the absolute latest versions:

```bash
pip install --upgrade pydantic pydantic-core pydantic-settings
```

However, Python 3.11 or 3.12 is strongly recommended for stability.

## Installation

```bash
cd server
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the `server` directory:

```bash
# Slack Webhook URL for approval notifications
# Get this from: https://api.slack.com/messaging/webhooks
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

To get a Slack webhook URL:
1. Go to https://api.slack.com/apps
2. Create a new app or select an existing one
3. Go to "Incoming Webhooks" and activate it
4. Click "Add New Webhook to Workspace"
5. Select the channel and copy the webhook URL

## Running the Server

```bash
# From the sudomode-ai directory:
uvicorn server.app.main:app --reload

# Or from the server directory:
uvicorn app.main:app --reload
```

## Slack Notifications

When an action requires approval (`REQUIRE_APPROVAL` status), the server will automatically send a formatted alert to your Slack channel. The notification includes:
- Resource and action details
- Amount (if applicable)
- Request ID for tracking
- A link to approve the request (placeholder for now)

The Slack notification is sent asynchronously and does not block the API response.

## Testing

See `test_examples.sh` for example curl commands.

To test Slack notifications, run the SDK demo with a high-value charge:
```bash
cd ../sdk
python examples/demo_agent.py
```


