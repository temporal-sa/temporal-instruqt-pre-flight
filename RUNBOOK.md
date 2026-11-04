# Runbook: Temporal pre-flight

Give guests a quick way to spot blocked browser tools before the webinar. The target is a few seconds of looking and clicking once the sandbox is ready.

## Before you start

Use the same invite/access mode planned for the webinar. The guest should use the same work laptop, browser, VPN and network they expect to use on the day. The invite must reach them before the event, while IT still has time to help.

The source repository and track are not registered yet. The draft Fieldkit resource is [deploy/instruqt-course.yaml](deploy/instruqt-course.yaml). Check its source URL and branch before adding it to `projects/test/instruqt/` in `temporal-fieldkit-platform`.

Fieldkit builds `instruqt/docker/Dockerfile` with repository-root context for `linux/amd64`. The image binding must target container `workshop`; `source.path` is `instruqt`. No secrets are required. The operator supplies the pullable public image; do not directly push the local image tag to Instruqt.

Validate the draft against the current platform schema using its `operator/cmd/validate-projects` tool before onboarding. Follow the platform’s normal test-to-live process. No fieldkit files, cloud resources or Instruqt tracks were changed during authoring.

## Start it

Open the published course invite and start the challenge. Track setup starts the web pages, editor and Temporal together, and waits for all five application ports before showing the lab. It also requests the editor page to warm it.

Launchpad embeds the real browser page, code-server and Temporal UI. It does not mark an iframe as successful just because its HTML loaded. Native full-size tabs are available when previews are small or embedding is blocked. The Terminal tab runs the clock command automatically when opened.

## The walkthrough

1. Look for Ziggy and choose **Yes, there’s Ziggy**.
2. Look for the editor and its welcome file; choose **Yes, editor’s here**. If necessary, open the full-size **Editor** tab and return.
3. Open **Terminal**. Confirm that **ZIGGY ONLINE** appears and its clock ticks. Return to Launchpad and choose **Yes, clock’s ticking**.
4. Look for the Temporal UI navigation and Workflows page. An empty list is expected. Choose **Yes, Temporal’s here**.
5. Once the automatic WebSocket round trip succeeds, Launchpad shows **Clear for launch**. Click Instruqt’s **Check** to complete the course.

A guest can choose the issue response at any time, including after saying yes. That revokes their completed result. **View readiness report** works for incomplete flights too. The guest reviews and copies the report; the course sends no messages on their behalf.

## When something goes wrong

| Symptom | Next step |
| --- | --- |
| The invite or sign-in page never loads | Use the guest guide below; this cannot be diagnosed from inside an inaccessible lab. Ask IT to review Instruqt’s platform and authentication domains. |
| Launchpad is blank | The assignment still explains how to report this. Capture the failed tab name, browser and time. |
| A preview is blank but its native tab works | Confirm from the native tab. Report the embedding issue to the organizer so they can investigate it. |
| Editor spins or terminal is blank/frozen | Ask IT to review secure WebSocket traffic through the company proxy and sandbox access on 443. |
| The live connection badge fails | Answers and the report still work if HTTPS works. Reload Launchpad after IT resolves the issue. |
| HTTP 572 from an application tab | Organizer: inspect setup logs, exposed ports, service health and image binding. Do not assume this is a laptop policy. |
| Every tab works for staff but fails on the guest’s work laptop | Ask IT to compare that device/browser policy and network path. Use only an approved alternative setup. |
| The lab never finishes creating | Organizer: check image pull and `/run/preflight/{supervisor,editor,temporal,launchpad}.log`. |

Keep company security controls enabled. Do not ask guests to turn off certificate validation, endpoint protection, a required VPN, or organization browser policy.

## Share before the event

Send [docs/guest-guide.md](docs/guest-guide.md) alongside the actual course invite. It includes the network-requirements link and a fallback message for guests who cannot open Instruqt at all. Set the organizer contact in the invitation; this repository has no assumed support email.

## Run it locally

Prerequisites: Docker, Docker Compose and `make`.

```sh
make demo       # clean image build; no source mounts; waits for healthy services
make terminal   # preview the clock that Instruqt starts in its native Terminal tab
make validate   # local Instruqt CLI configuration check
make test       # isolated API tests in a container
make logs       # sandbox service logs
make reset      # replace the local container and discard this local run
make down
```

Open http://localhost:5000. Local clock viewing via `make terminal` substitutes for the native Instruqt Terminal tab only in contributor testing. Instruqt’s browser terminal still requires a real learner play.

## Acceptance before publication

Instruqt’s local validator, Compose configuration validation and the current Fieldkit project validator passed. The authoring workspace could not access the Docker socket or computer-use permissions. The following runtime and visual checks are pending; do not describe the course as tested on Instruqt until they pass.

- Run `make test`, then `make demo` from a clean checkout. Confirm all previews and the welcome file actually render, the clock changes and all four confirmations complete.
- At a 1280×720 browser window and in the narrower Instruqt service frame, scroll Launchpad to the step 3 and 4 buttons and the readiness report. Check keyboard access too. The page must scroll even though the shared component stylesheet defaults to a fixed booth layout.
- Confirm Ziggy bobs and blinks and the stars move. **Pause animation** on Launchpad must pause both its background and the Ziggy preview; the standalone Browser tab also has its own control. Enable reduced motion and confirm the mascot and stars stay still.
- Use two browser contexts. Confirm their answers and reports stay separate. Refresh one context; its answers should return where session storage is allowed. With storage blocked, the check should still work for that page visit.
- Block `/ws` in browser dev tools. Four visual confirmations must not produce clearance. Confirm the incomplete report remains available. Restore the connection and reload; it should complete after a real round trip.
- Test a failed page and an answer changed from yes to issue. Neither should produce a completed readiness result.
- Stop the editor or Temporal process. The supervisor should stop the other services and log the failed child; setup must fail if any required port is absent. Restart the sandbox for recovery.
- Run a real Instruqt learner play from a managed work laptop, including the native Terminal tab and full-size service tabs. Check current Chrome/Edge and another supported browser. Confirm whether nested preview frames are usable behind Instruqt’s auth proxy.
- Exercise the same invite mode and corporate VPN/network that attendees use. Confirm the assignment’s fallback path works when Launchpad is blocked.
- Validate the Fieldkit resource against the platform schema and publish to its test environment first.

`instruqt track test` runs lifecycle scripts, including a synthetic solve. The solve script here intentionally exits with an explanation because a sandbox script cannot provide evidence that a guest saw an application. Use the API tests for readiness logic and a real browser play for the course.

## Show it in code

| Guest behavior | Source |
| --- | --- |
| Four yes/issue choices and live previews | [app/static/index.html](app/static/index.html), [app/static/flight.js](app/static/flight.js) |
| Server-backed answers, socket echo and honest reports | [app/server.py](app/server.py) |
| Automatic editor welcome file and service startup | [app/supervise.py](app/supervise.py), [instruqt/docker/start.sh](instruqt/docker/start.sh) |
| Real native terminal with automatic clock | [assignment.md](instruqt/01-launch-clearance/assignment.md), [terminal.sh](instruqt/docker/terminal.sh) |
| Instruqt completion gate | [check-workshop](instruqt/01-launch-clearance/check-workshop) |

These are working-tree links. Add commit permalinks once the project is published.

## Reset and tear down

Start a new Instruqt play for a clean guest sandbox. Instruqt destroys the per-guest container at the end of its lifetime. Reports are kept only in that container; they are not sent to a central reporting service. Instruqt tracks its own challenge completion normally.

Local `make reset` affects only this Compose project. No cloud or production reset is provided.
