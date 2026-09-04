# Ripple Privacy Policy — Development / Hackathon Build

Effective date: 4 September 2026

Ripple is a development-stage Alexa+ add-on and MCP service built for the Amazon Developer Hackathon. The currently deployed public demo is designed to demonstrate consequence analysis, exact approval, bounded execution, receipts, and replay safety. Its ride, dining, grocery, pet-care, and calendar provider actions are simulated; it does not place real bookings, charges, or provider writes.

## Data used

When you use Ripple, the service may process the plan change you provide, the downstream commitments generated for the demo scenario, the repair proposal, the approval decision, execution receipts, OAuth tokens used for the active session, and technical request metadata needed to operate and secure the service.

Ripple does not ask Alexa+ to provide contacts, precise location, payment-card details, health information, or advertising identifiers for the current development experience.

## Purpose

Data is used only to interpret the reported change, calculate downstream consequences, present an exact repair proposal, enforce the approval boundary, execute the approved simulated actions, prevent duplicate execution, and diagnose reliability or security issues.

## Retention

The current public Railway deployment uses short-lived in-memory MCP sessions with a default inactivity lifetime of one hour. Access tokens expire after one hour; authorization codes expire after five minutes; demo refresh tokens expire after 30 days. Process restarts may delete in-memory state earlier. Hosting infrastructure may retain limited operational logs according to its service policies.

If Ripple is moved to the planned durable AWS runtime, this policy will be updated before public certification to describe the durable state, retention period, and deletion mechanism before real customer data is accepted.

## Sharing

Ripple does not sell customer data. In the current development build, provider actions are simulated locally. Infrastructure providers may process request and operational data only as needed to host or secure the service.

## Security

Ripple uses HTTPS, OAuth authorization code with PKCE S256 for user-level access, service-level client credentials, exact-plan approval binding, and replay-safe execution controls. No system can be guaranteed completely secure.

## Your choices

Do not submit sensitive personal information to this development build. You can end an MCP session at any time; inactive sessions expire automatically. For development-stage questions, use the public repository issue tracker and do not post personal or secret information in a public issue.

Repository: https://github.com/rarescos-pixel/ripple-agentic-plan-repair
