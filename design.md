# SudoMode - Design Document

## System Architecture

### High-Level Architecture

```
┌─────────────────┐
│   AI Agent      │
│   (Client)      │
└────────┬────────┘
         │ 1. Intent Request
         │ (resource, action, args)
         ▼
┌─────────────────────────────────────────┐
│         SudoMode Proxy Server           │
│  ┌───────────────────────────────────┐  │
│  │      REST API (FastAPI)           │  │
│  │  /v1/govern, /v1/requests/*       │  │
│  └──────────┬────────────────────────┘  │
│             │                            │
│  ┌──────────▼────────────────────────┐  │
│  │     Policy Engine                 │  │
│  │  - Load YAML policies             │  │
│  │  - Match resource/action          │  │
│  │  - Evaluate conditions            │  │
│  │  - Return decision                │  │
│  └──────────┬────────────────────────┘  │
│             │                            │
│  ┌──────────▼────────────────────────┐  │
│  │     Request Store                 │  │
│  │  - In-memory storage              │  │
│  │  - Track pending requests         │  │
│  │  - Update status                  │  │
│  └───────────────────────────────────┘  │
│                                          │
│  ┌───────────────────────────────────┐  │
│  │     Slack Service                 │  │
│  │  - Send notifications             │  │
│  │  - Format alerts                  │  │
│  └───────────────────────────────────┘  │
└─────────┬────────────────────────────────┘
          │
          │ 2. Notify (if approval needed)
          ▼
┌─────────────────────┐
│  Human Reviewers    │
│  - Slack            │
│  - Dashboard        │
└─────────┬───────────┘
          │ 3. Approve/Reject
          ▼
┌─────────────────────┐
│  React Dashboard    │
│  - View requests    │
│  - Approve/Reject   │
│  - Real-time poll   │
└─────────────────────┘
```

## Component Design

### 1. Backend Server (FastAPI)

#### 1.1 API Layer (`server/app/main.py`)

**Responsibilities:**
- Handle HTTP requests
- Route to appropriate handlers
- Manage CORS
- Coordinate between engine, store, and services

**Endpoints:**

```python
POST /v1/govern
  Request: GovernanceRequest
    - resource: str
    - action: str
    - args: Dict[str, Any]
  Response: GovernanceResponse
    - status: "ALLOW" | "DENY" | "REQUIRE_APPROVAL"
    - reason: str
    - request_id: Optional[str]

GET /v1/requests
  Response: { requests: List[RequestData] }

GET /v1/requests/{request_id}
  Response: RequestData
    - id: str
    - resource: str
    - action: str
    - args: Dict
    - status: "PENDING" | "APPROVED" | "REJECTED"
    - reason: str
    - timestamp: str

POST /v1/requests/{request_id}/approve
  Response: { status: "success", message: str, request: RequestData }

POST /v1/requests/{request_id}/reject
  Response: { status: "success", message: str }

GET /health
  Response: { status: "healthy" }
```

#### 1.2 Policy Engine (`server/app/core/engine.py`)

**Responsibilities:**
- Load and parse YAML policies
- Evaluate requests against rules
- Match resource/action patterns
- Evaluate conditional expressions
- Return governance decisions

**Key Classes:**

```python
class PolicyEngine:
    def __init__(self, policies_file: Optional[str] = None)
    def _load_policies(self) -> Dict[str, Any]
    def _matches_resource(self, rule_resource: str, request_resource: str) -> bool
    def _matches_action(self, rule_action: str, request_action: str) -> bool
    def _evaluate_condition(self, condition: Optional[str], request: GovernanceRequest) -> bool
    def evaluate(self, request: GovernanceRequest) -> GovernanceResponse
```

**Policy Evaluation Algorithm:**

```
1. Load rules from YAML file
2. For each rule in order:
   a. Check if resource matches (exact or wildcard)
   b. Check if action matches (exact or wildcard)
   c. If condition exists, evaluate it safely
   d. If all match, return rule's decision
3. If no rule matches, return DENY (fail-safe)
```

**Condition Evaluation:**
- Uses `simpleeval` library for safe expression evaluation
- Prevents code injection
- Provides access to: `args`, `resource`, `action`
- Example: `args.amount > 100`

#### 1.3 Request Store (`server/app/core/store.py`)

**Responsibilities:**
- Store pending approval requests
- Track request status
- Provide CRUD operations
- In-memory storage (dict-based)

**Key Functions:**

```python
def add_request(request_id: str, request: GovernanceRequest, status: str, reason: str)
def get_request(request_id: str) -> Optional[Dict]
def get_all_requests() -> List[Dict]
def update_request_status(request_id: str, status: str)
def remove_request(request_id: str)
```

**Data Structure:**

```python
{
  "request_id": {
    "id": str,
    "resource": str,
    "action": str,
    "args": Dict[str, Any],
    "status": "PENDING" | "APPROVED" | "REJECTED",
    "reason": str,
    "timestamp": str (ISO format)
  }
}
```

#### 1.4 Slack Service (`server/app/services/slack.py`)

**Responsibilities:**
- Send formatted notifications to Slack
- Handle webhook communication
- Format alert messages
- Fail gracefully on errors

**Key Classes:**

```python
class SlackService:
    def __init__(self, webhook_url: Optional[str] = None)
    async def send_alert(self, request_data: GovernanceRequest, rule_reason: str, request_id: str)
    def _format_message(self, request_data: GovernanceRequest, rule_reason: str, request_id: str) -> Dict
```

**Message Format:**
- Rich formatting with blocks
- Color-coded (warning yellow)
- Includes resource, action, arguments
- Shows reason and request ID
- Links to dashboard

#### 1.5 Configuration (`server/app/core/config.py`)

**Responsibilities:**
- Load environment variables
- Provide configuration settings
- Locate policies file

**Settings:**
- `POLICIES_FILE`: Path to policies YAML
- `SLACK_WEBHOOK_URL`: Optional Slack webhook
- Server configuration (host, port, etc.)

### 2. Frontend Dashboard (React + Vite)

#### 2.1 Application Structure

```
dashboard/
├── src/
│   ├── App.jsx              # Main application component
│   ├── components/
│   │   └── RequestCard.jsx  # Individual request card
│   ├── main.jsx             # Entry point
│   └── index.css            # Global styles (Tailwind)
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

#### 2.2 App Component (`App.jsx`)

**Responsibilities:**
- Fetch requests from API
- Poll for updates (2-second interval)
- Handle approve/reject actions
- Display pending and recent requests
- Error handling and loading states

**State Management:**

```javascript
const [requests, setRequests] = useState([])
const [loading, setLoading] = useState(true)
const [error, setError] = useState(null)
```

**Key Functions:**

```javascript
fetchRequests()           // GET /v1/requests
handleApprove(requestId)  // POST /v1/requests/{id}/approve
handleReject(requestId)   // POST /v1/requests/{id}/reject
```

**UI Sections:**
1. Header: Title, branding, pending count
2. Pending Approvals: Grid of pending request cards
3. Recent Activity: Grid of approved/rejected requests
4. Empty State: Shown when no pending requests
5. Error State: Shown on API failures

#### 2.3 RequestCard Component

**Responsibilities:**
- Display single request details
- Show status badge
- Provide approve/reject buttons
- Format arguments and timestamps

**Props:**
- `request`: Request data object
- `onApprove`: Callback for approve action
- `onReject`: Callback for reject action

**Visual Design:**
- Dark theme (cyberpunk/security aesthetic)
- Color-coded status badges
- Responsive card layout
- Hover effects and transitions

### 3. Python SDK

#### 3.1 Client (`sdk/sudomode/client.py`)

**Responsibilities:**
- Communicate with SudoMode server
- Handle governance workflow
- Implement long-polling for approvals
- Provide simple API for agents

**Key Classes:**

```python
class SudoClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None)
    def check(self, resource: str, action: str, args: Optional[Dict] = None) -> GovernanceResponse
    def get_request_status(self, request_id: str) -> Dict[str, Any]
    def execute(self, resource: str, action: str, args: Optional[Dict] = None, poll_interval: int = 2) -> bool
    def close()
```

**Execute Method Flow:**

```
1. Call check() to evaluate request
2. If ALLOW: return True immediately
3. If DENY: raise PermissionError
4. If REQUIRE_APPROVAL:
   a. Log approval required message
   b. Start polling loop:
      - Sleep for poll_interval seconds
      - Call get_request_status()
      - If APPROVED: return True
      - If REJECTED: raise PermissionError
      - If PENDING: continue loop
```

**Error Handling:**
- `PermissionError`: Raised for DENY or REJECTED
- `ValueError`: Raised for missing request_id
- `httpx.HTTPError`: Raised for network/API errors

#### 3.2 Example Agents

**demo_agent.py:**
- Demonstrates basic governance scenarios
- Shows ALLOW, DENY, REQUIRE_APPROVAL flows
- Includes logging and error handling

**bank_agent.py:**
- Realistic banking agent example
- Shows integration with business logic
- Demonstrates proper error handling
- Includes multiple operation types

## Data Models

### GovernanceRequest

```python
class GovernanceRequest(BaseModel):
    resource: str        # e.g., "database", "stripe.charge"
    action: str          # e.g., "read", "delete", "charge"
    args: Dict[str, Any] # e.g., {"amount": 100}
```

### GovernanceResponse

```python
class GovernanceResponse(BaseModel):
    status: Literal["ALLOW", "DENY", "REQUIRE_APPROVAL"]
    reason: str
    request_id: Optional[str] = None
```

### Policy Rule

```yaml
name: string              # Unique identifier
description: string       # Human-readable description
resource: string          # Resource pattern (exact or "*")
action: string            # Action pattern (exact or "*")
condition: string         # Optional Python expression
decision: string          # "ALLOW", "DENY", or "REQUIRE_APPROVAL"
reason: string            # Explanation for decision
```

## Security Considerations

### 1. Safe Expression Evaluation
- Use `simpleeval` library (not `eval()`)
- Restrict available functions and names
- Prevent code injection attacks
- Fail closed on evaluation errors

### 2. Input Validation
- Use Pydantic for all API models
- Validate types and required fields
- Sanitize user inputs
- Reject malformed requests

### 3. Default Deny
- No rule match → DENY
- Missing policy file → empty ruleset → DENY
- Evaluation error → DENY
- Fail-safe approach

### 4. CORS Protection
- Explicit origin whitelist
- No wildcard origins in production
- Credentials support for authenticated requests

### 5. API Authentication (Future)
- Support optional API key authentication
- Bearer token in Authorization header
- Per-client access control

## Performance Considerations

### 1. Policy Evaluation
- In-memory rule storage
- Sequential rule evaluation (acceptable for typical rulesets)
- Early exit on first match
- Condition evaluation cached per request

### 2. Request Storage
- In-memory dict (fast access)
- No persistence (acceptable for MVP)
- Future: Redis or database for persistence

### 3. Dashboard Polling
- 2-second interval (balance between real-time and load)
- Client-side polling (no WebSocket overhead)
- Efficient JSON serialization

### 4. SDK Long-Polling
- Configurable poll interval
- Blocking wait (acceptable for agent use case)
- HTTP connection reuse

## Deployment Architecture

### Development Setup

```
Terminal 1: Backend Server
  cd server
  uvicorn app.main:app --reload
  → http://localhost:8000

Terminal 2: Frontend Dashboard
  cd dashboard
  npm run dev
  → http://localhost:5173

Terminal 3: Agent/SDK
  cd sdk
  python examples/demo_agent.py
```

### Production Considerations (Future)

1. **Backend:**
   - Deploy with Gunicorn + Uvicorn workers
   - Use environment variables for configuration
   - Add persistent storage (PostgreSQL/Redis)
   - Implement API authentication
   - Add rate limiting

2. **Frontend:**
   - Build static assets (`npm run build`)
   - Serve via CDN or Nginx
   - Configure production API URL
   - Add authentication

3. **Infrastructure:**
   - Docker containers
   - Kubernetes orchestration
   - Load balancing
   - Monitoring and logging
   - Backup and recovery

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation
- **PyYAML**: Policy file parsing
- **simpleeval**: Safe expression evaluation
- **httpx**: HTTP client (for Slack)
- **Uvicorn**: ASGI server

### Frontend
- **React 19**: UI library
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Utility-first styling
- **JavaScript/JSX**: Language

### SDK
- **httpx**: HTTP client
- **Pydantic**: Data validation

### Development
- **Python 3.10+**: Backend language
- **Node.js**: Frontend tooling
- **npm**: Package management

## Testing Strategy

### Unit Tests (Future)
- Policy engine rule matching
- Condition evaluation
- Request store operations
- API endpoint handlers

### Integration Tests (Future)
- End-to-end governance flow
- SDK client integration
- Dashboard API communication

### Manual Testing
- Example agents (demo_agent.py, bank_agent.py)
- Dashboard UI testing
- Policy configuration testing

## Monitoring and Observability (Future)

### Logging
- Request/response logging
- Policy evaluation decisions
- Error tracking
- Performance metrics

### Metrics
- Request count by decision type
- Average evaluation time
- Approval wait time
- Error rates

### Alerting
- Failed policy evaluations
- High error rates
- Slow response times
- Slack notification failures

## Future Enhancements

### Short-term
1. Docker Compose setup
2. Persistent storage (PostgreSQL/Redis)
3. Webhook callbacks for approvals
4. Advanced policy conditions (regex, time-based)

### Medium-term
1. Multi-tenant support
2. Policy versioning and rollback
3. Go/TypeScript SDKs
4. Integration with AWS SDK, GCP, etc.

### Long-term
1. AI-powered risk scoring
2. Automated policy suggestions
3. Compliance reporting (SOC2, GDPR)
4. Hosted cloud version
5. CI/CD pipeline integration
