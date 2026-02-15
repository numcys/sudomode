# SudoMode - Requirements Document

## Project Overview

SudoMode is a governance and authorization middleware proxy for AI agents that intercepts high-risk actions and enforces human approval before execution. It acts as a "sudo command" for AI agents, preventing unintended consequences from prompt injection, bugs, or hallucinations.

## Problem Statement

AI agents with direct access to critical systems (payment APIs, databases, cloud services, authentication systems) pose significant risks:
- Prompt injection attacks can manipulate agent behavior
- LLM hallucinations may trigger destructive operations
- Bugs in agent logic can cause catastrophic damage
- Direct API access enables operations like `db.drop_table()` or `stripe.charge(amount=999999)`

## Solution

SudoMode implements an intent-based governance layer where:
1. Agents send intents (what they want to do) instead of executing directly
2. A policy engine evaluates each intent against configurable rules
3. High-risk actions pause for human approval
4. Only approved actions execute against real APIs

## Functional Requirements

### 1. Policy Engine
- **FR-1.1**: Evaluate governance requests against YAML-defined policy rules
- **FR-1.2**: Support resource pattern matching (exact match and wildcard `*`)
- **FR-1.3**: Support action pattern matching (exact match and wildcard `*`)
- **FR-1.4**: Evaluate conditional expressions using request arguments (e.g., `args.amount > 100`)
- **FR-1.5**: Return one of three decisions: ALLOW, DENY, or REQUIRE_APPROVAL
- **FR-1.6**: Apply first-match-wins rule evaluation order
- **FR-1.7**: Default to DENY when no rules match (fail-safe)
- **FR-1.8**: Provide human-readable reasons for all decisions

### 2. Request Management
- **FR-2.1**: Generate unique IDs for approval requests
- **FR-2.2**: Store pending requests with status tracking (PENDING, APPROVED, REJECTED)
- **FR-2.3**: Retrieve request status by ID
- **FR-2.4**: List all pending requests
- **FR-2.5**: Update request status (approve/reject)
- **FR-2.6**: Maintain audit trail of all governance decisions

### 3. REST API
- **FR-3.1**: Provide `/v1/govern` endpoint for policy evaluation
- **FR-3.2**: Provide `/v1/requests` endpoint to list all requests
- **FR-3.3**: Provide `/v1/requests/{id}` endpoint to get request status
- **FR-3.4**: Provide `/v1/requests/{id}/approve` endpoint to approve requests
- **FR-3.5**: Provide `/v1/requests/{id}/reject` endpoint to reject requests
- **FR-3.6**: Provide `/health` endpoint for health checks
- **FR-3.7**: Support CORS for frontend dashboard access

### 4. Python SDK
- **FR-4.1**: Provide `SudoClient` class for server communication
- **FR-4.2**: Implement `check()` method for low-level permission checks
- **FR-4.3**: Implement `execute()` method with automatic approval workflow handling
- **FR-4.4**: Support long-polling for approval requests
- **FR-4.5**: Raise `PermissionError` for denied/rejected actions
- **FR-4.6**: Return `True` for allowed/approved actions
- **FR-4.7**: Support context manager protocol for resource cleanup
- **FR-4.8**: Provide configurable polling intervals

### 5. Dashboard UI
- **FR-5.1**: Display pending approval requests in real-time
- **FR-5.2**: Show request details (resource, action, arguments, reason)
- **FR-5.3**: Provide approve/reject buttons for pending requests
- **FR-5.4**: Auto-refresh request list (2-second polling)
- **FR-5.5**: Display request count and status indicators
- **FR-5.6**: Show recent activity (approved/rejected requests)
- **FR-5.7**: Handle API errors gracefully with user feedback

### 6. Notification System
- **FR-6.1**: Send Slack notifications when approval is required
- **FR-6.2**: Include request details in notifications (resource, action, args, reason)
- **FR-6.3**: Include request ID for tracking
- **FR-6.4**: Support optional Slack integration (configurable via environment)
- **FR-6.5**: Fail gracefully if Slack notification fails (don't block request)

### 7. Configuration
- **FR-7.1**: Load policies from YAML file (`policies.yaml`)
- **FR-7.2**: Support environment-based configuration (`.env` file)
- **FR-7.3**: Provide example policy configuration (`policies.yaml.example`)
- **FR-7.4**: Support Slack webhook URL configuration
- **FR-7.5**: Allow custom policies file path

## Non-Functional Requirements

### Performance
- **NFR-1.1**: Policy evaluation should complete in < 100ms
- **NFR-1.2**: API endpoints should respond in < 200ms (excluding approval wait time)
- **NFR-1.3**: Dashboard should poll efficiently without overwhelming the server
- **NFR-1.4**: Support concurrent request evaluation

### Security
- **NFR-2.1**: Use safe expression evaluation (simpleeval) for policy conditions
- **NFR-2.2**: Prevent code injection in policy conditions
- **NFR-2.3**: Default to DENY for security (fail-safe)
- **NFR-2.4**: Support optional API key authentication
- **NFR-2.5**: Validate all input data using Pydantic models
- **NFR-2.6**: Protect against CORS attacks with explicit origin whitelist

### Reliability
- **NFR-3.1**: Handle missing policy files gracefully (empty ruleset)
- **NFR-3.2**: Handle YAML parsing errors with clear error messages
- **NFR-3.3**: Continue operation if Slack notifications fail
- **NFR-3.4**: Provide clear error messages for all failure scenarios
- **NFR-3.5**: Support automatic reconnection in SDK client

### Usability
- **NFR-4.1**: Provide clear, human-readable policy syntax
- **NFR-4.2**: Include comprehensive examples and documentation
- **NFR-4.3**: Provide intuitive dashboard UI with dark theme
- **NFR-4.4**: Support one-line SDK integration
- **NFR-4.5**: Include detailed logging for debugging

### Maintainability
- **NFR-5.1**: Use type hints throughout Python codebase
- **NFR-5.2**: Follow PEP 8 style guidelines
- **NFR-5.3**: Include docstrings for all public functions/classes
- **NFR-5.4**: Separate concerns (engine, API, storage, services)
- **NFR-5.5**: Use modern frameworks (FastAPI, React)

### Compatibility
- **NFR-6.1**: Support Python 3.10, 3.11, 3.12
- **NFR-6.2**: Support modern browsers (Chrome, Firefox, Safari, Edge)
- **NFR-6.3**: Work on macOS, Linux, and Windows
- **NFR-6.4**: Use cross-platform dependencies

## User Stories

### Agent Developer
- As an agent developer, I want to protect my agent from executing dangerous operations so that I can prevent catastrophic damage
- As an agent developer, I want simple SDK integration so that I can add governance with minimal code changes
- As an agent developer, I want clear error messages so that I can debug permission issues quickly

### Security Administrator
- As a security admin, I want to define policies in YAML so that I can configure governance without code changes
- As a security admin, I want to review high-risk actions before execution so that I can prevent unauthorized operations
- As a security admin, I want an audit trail so that I can track all governance decisions

### Operations Team
- As an ops team member, I want real-time notifications so that I can respond quickly to approval requests
- As an ops team member, I want a dashboard to manage requests so that I can approve/reject actions efficiently
- As an ops team member, I want to see request history so that I can audit agent behavior

## Out of Scope (Future Enhancements)

- Multi-tenant support
- Webhook callbacks for approvals
- Advanced policy conditions (regex, time-based rules)
- AI-powered risk scoring
- Policy versioning and rollback
- Integration with additional services (AWS SDK, GCP, etc.)
- Go/TypeScript SDKs
- Compliance reporting (SOC2, GDPR)
- Docker Compose setup
- Hosted cloud version

## Success Criteria

1. Agent can integrate SudoMode with < 5 lines of code
2. Policy engine evaluates requests in < 100ms
3. Dashboard displays pending requests within 2 seconds
4. SDK handles approval workflow automatically (long-polling)
5. System defaults to DENY for safety
6. All critical operations require explicit policy rules
7. Comprehensive documentation and examples provided
8. Zero security vulnerabilities in policy evaluation
