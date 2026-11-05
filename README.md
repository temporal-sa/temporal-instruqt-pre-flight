# Temporal pre-flight

Check that a guest’s workshop laptop can display Ziggy, the code editor, live terminal output and Temporal UI. Everything starts automatically; the guest just confirms what they see.

The course has one challenge. Launchpad is a step-by-step wizard: an introduction, four one-at-a-time visual confirmations (browser image, editor, terminal, Temporal UI) and a results page. It also checks a browser WebSocket round trip. A blocked page gets specific help and a readiness report the guest can copy to their organizer.

Ziggy bobs and blinks against an animated starfield. Use **Pause animation** to stop the motion; the page also respects your system’s reduced-motion setting. Launchpad scrolls inside the Instruqt frame so all four checks remain reachable.

## Run it

For contributors: Docker, Docker Compose and `make`.

```sh
make demo
```

Open [Launchpad](http://localhost:5000). `make terminal` previews the automatic terminal clock locally. In Instruqt, the native Terminal tab starts it automatically.

Guests need a browser and the course invite. They install nothing and run no commands.

## Build and publish with Fieldkit

The sandbox is one container, with no VM, nested Docker or external credentials. Fieldkit builds [instruqt/docker/Dockerfile](instruqt/docker/Dockerfile) from the repository root and replaces the `workshop` image in [config.yml](instruqt/config.yml).

[deploy/instruqt-course.yaml](deploy/instruqt-course.yaml) is a draft matching the local `temporal-fieldkit-platform` contract. Its source URL assumes a future `temporal-sa/temporal-instruqt-pre-flight` repository. Set the actual source repository and branch before adding it to Fieldkit’s test catalog. This project has not been published or registered.

```sh
make validate   # local Instruqt configuration validation
make test       # readiness API tests, in a container
```

Run a real learner play before publication. `instruqt track test` runs sandbox scripts; it cannot check a guest’s browser. This track deliberately refuses to synthesize a visual pass with a solve script.

Setup, reset and event checks: [RUNBOOK.md](RUNBOOK.md). Research and the corporate-network checklist: [docs/instruqt-research.md](docs/instruqt-research.md).

## Scope and notes

This is a point-in-time visual check on the browser and network used for the pre-flight. It does not verify typing, editing, clipboard permissions, long-lived connections, LLM calls, workshop secrets, or the lab exercises. An empty Temporal Workflow list is expected.

The container exposes the same five application ports as the inspected AI Agents Webinar. Its browser/editor/terminal surfaces exercise the same kinds of access; it does not contain the AI workshop runtime.

The buildkit’s `DemoProject` and crashable Worker patterns do not apply to this `InstruqtCourse`: Instruqt provides a separate disposable container per guest, and this course starts no Workflows or Workers. [docs/catalog.md](docs/catalog.md) records the Fieldkit mapping.

The sandbox has unauthenticated internal services behind Instruqt’s learner authentication. Local Compose binds ports to loopback. Keep this image behind that gate.

Temporal logo and Ziggy assets are Temporal trademarks and are not covered by the code’s MIT license. Bundled fonts retain their SIL Open Font Licenses under `app/static/assets/fonts/`.

Instruqt configuration validation, Compose configuration validation and Fieldkit’s current project validator passed. Container build and runtime tests could not run because Docker socket access was denied; visual review was also blocked by unavailable computer-use permissions. See the runbook for the remaining acceptance checks.
