# Instruqt runs the lab remotely; the guest supplies the browser connection

Research checked on 2026-11-04 against Instruqt’s official documentation and the local AI Agents Webinar repository.

## What Instruqt provides

A track combines metadata in `track.yml`, sandbox infrastructure in `config.yml`, challenge instructions and tabs in `assignment.md`, and lifecycle scripts. Each guest play gets its own remote sandbox. A container can provide terminal and web services without requiring a VM or local guest installs. See [configuration files](https://docs.instruqt.com/reference/cli/configuration-files) and [sandbox hosts](https://docs.instruqt.com/sandboxes/hosts).

Service tabs use an authenticated HTTPS proxy to reach sandbox applications. A documented hostname is `host-port-participant.env.play.instruqt.com`, with an optional protocol override after the port. Backend services must listen on `0.0.0.0` and container ports must be exposed in `config.yml`. HTTPS terminates at the proxy; this course’s services use HTTP inside the sandbox. See [networking](https://docs.instruqt.com/reference/platform/networking) and [challenge tabs](https://docs.instruqt.com/tracks/challenges/challenge-tabs).

Terminal sessions use secure WebSockets. Company proxies can allow the platform page while blocking an application hostname or live connection. Consequently, a successful command or HTTP probe inside the sandbox cannot prove that an attendee’s laptop can use the lab. This is the design reason for real browser surfaces and guest confirmations.

## What the webinar actually uses

Inspected `~/Source/ai-agents-webinar/instruqt/track.yml`, `config.yml`, `docker/Dockerfile`, track setup and challenge assignments. The course has three progressive AI-agent modules and one sandbox container named `workshop`.

| Surface | Webinar port | Pre-flight |
| --- | --- | --- |
| Network control panel | 5000 | Launchpad: HTML, JS, images, JSON requests and a WebSocket echo |
| code-server editor | 8080 | Real code-server with a prepared welcome file |
| Multi-agent architecture | 8090 | Real browser page showing Ziggy |
| Human-input architecture | 8092 | Automatic image request through the equivalent sandbox hostname |
| Temporal UI | 8233 | Real Temporal dev-server UI; empty Workflow list is expected |
| Instruqt terminal tabs | Instruqt transport | Native terminal command starts automatically and prints a ticking clock |

The webinar’s local-run README lists Python, uv, Node and API-key prerequisites. Its Instruqt image bakes those tools and dependencies in. Guests taking the hosted pre-flight do not need them locally. The full webinar also relies on sandbox-side services and a LiteLLM broker secret; this small course does not verify them or spend model tokens.

## Corporate-network checklist

Give IT the current official [network access list](https://docs.instruqt.com/reference/platform/third-party-network-access), rather than a permanently copied allowlist. At research time it identifies these required groups:

| Purpose | Endpoints / traffic |
| --- | --- |
| Core platform | `https://play.instruqt.com`, `https://ping.instruqt.com` on 443 |
| Static resources | `https://cdn.instruqt.com`, `https://static.instruqt.com` on 443 |
| Sandbox apps and terminal sessions | `https://*.env.play.instruqt.com`, `wss://*.env.play.instruqt.com` on 443 |
| Fonts used by the platform | `fonts.googleapis.com`, `fonts.gstatic.com` on 443 |
| Firebase authentication/session services | `firebase.googleapis.com`, `firebaseinstallations.googleapis.com`, `identitytoolkit.googleapis.com`, `securetoken.googleapis.com` on 443 |

The docs list `*.instruqt.io` for optional direct ingress to VMs. This container course uses the authenticated web proxy; it does not require opening arbitrary high ports on the guest’s laptop. The app ports above are internal sandbox ports, all reached by the browser through HTTPS on 443.

Instruqt recommends current browsers, a stable connection of at least 8 Mbps and a screen of at least 1280×720. See [client requirements](https://docs.instruqt.com/reference/platform/requirements). The pre-flight does not run a speed test or enforce display size.

## What counts as passing

The guest confirms all four visible surfaces and the browser completes a nonce echo over the real WebSocket endpoint. HTML load events and sandbox HTTP health checks never supply a visual confirmation. A later issue response revokes completion. Reports explicitly say they cover visibility and one observed connection round trip.

Instruqt’s [automated track test](https://docs.instruqt.com/tracks/manage/test-a-track) runs setup, an initially failing check, solve, then a successful check. That tests lifecycle behavior, not an actual corporate laptop. The course’s solve script deliberately refuses to fabricate visual evidence. Use container API tests and a real learner play.

Testing the exact webinar invite and runtime is still necessary before each event. A passed pre-flight does not establish that the later workshop’s credentials, LLM gateway, third-party tools, typing, editing or long-lived sessions will work.
