# SudoMode Dashboard

React dashboard for monitoring and approving AI agent governance requests.

## Features

- **Real-time Updates**: Automatically polls the backend API every 2 seconds
- **Dark Theme**: Cyberpunk/enterprise security aesthetic with dark mode
- **Request Management**: View, approve, or reject pending governance requests
- **Risk Indicators**: Visual badges showing risk levels
- **Responsive Design**: Works on desktop and mobile devices

## Setup

1. Install dependencies:
```bash
npm install
```

2. Make sure the backend server is running on `http://localhost:8000`

3. Start the development server:
```bash
npm run dev
```

4. Open your browser to the URL shown (typically `http://localhost:5173`)

## Usage

1. **View Pending Requests**: The dashboard automatically displays all pending requests that require approval
2. **Approve Request**: Click the green "AUTHORIZE" button to approve an action
3. **Reject Request**: Click the red "BLOCK" button to reject an action
4. **Real-time Updates**: New requests appear automatically as they come in

## Testing

To test the dashboard:

1. Start the backend server:
```bash
cd ../server
uvicorn app.main:app --reload
```

2. Start the dashboard:
```bash
npm run dev
```

3. Run the SDK demo to create a pending request:
```bash
cd ../sdk
python examples/demo_agent.py
```

4. Watch the request appear in the dashboard automatically!

## API Endpoints Used

- `GET /v1/requests` - Fetch all requests
- `POST /v1/requests/{id}/approve` - Approve a request
- `POST /v1/requests/{id}/reject` - Reject a request

## Tech Stack

- **React 19** - UI framework
- **Vite** - Build tool
- **Tailwind CSS 3** - Styling
- **Fetch API** - HTTP requests
