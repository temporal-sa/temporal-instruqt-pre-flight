# Fieldkit course mapping

This project is an `InstruqtCourse`, using the current contract in `~/Source/temporal-fieldkit-platform`, inspected on 2026-11-04. It follows the neighboring `projects/test/instruqt/ai-agents-webinar.yaml` course and `operator/reference/schemas/instruqt-course.schema.json`.

| Contract | Choice |
| --- | --- |
| Catalog kind | `registry.tmprl-demo.cloud/v1alpha1`, `InstruqtCourse` |
| Build | One `linux/amd64` Dockerfile build from repository-root context |
| Dockerfile | `instruqt/docker/Dockerfile` |
| Course files | `source.path: instruqt` |
| Image binding | `images.workshop.container: workshop`, matching `config.yml` |
| Sandbox | Instruqt container `workshop`, 4096 MB; no virtual machines |
| Ports | 5000 Launchpad; 8080 code-server; 8090/8092 browser pages; 8233 Temporal UI |
| Public path | Instruqt’s authenticated HTTPS/WSS sandbox proxy on 443 |
| Identity and isolation | Instruqt provides a separate sandbox per guest play. Within a sandbox, each browser has an opaque random session token. |
| Browser state | Namespaced session storage when available; in-memory token fallback if blocked. SQLite keyed by token stores confirmations in the disposable sandbox. |
| Temporal configuration | A sandbox-only Temporal dev server. CLI config loading is disabled. No Workflows, Activities, Workers or Task Queues are started. |
| Secrets | None; no LLM API keys, Cloud credentials or broker calls |
| Health | `/healthz` for Launchpad; setup additionally probes all five ports and warms the editor |
| Reset | New Instruqt play; no shared deployment or other guest’s data to reset |
| Limits | 15-minute sandbox lifetime; 10-minute idle timeout. Guest checks are intended to take a few seconds once ready. |

The source URL in [the draft resource](../deploy/instruqt-course.yaml) is a proposed future location. Confirm the repository and branch before onboarding. Its owner must be one of the owners accepted by Fieldkit (`temporal-sa`, `temporalio`, `temporal-community`). The existing track has no assigned IDs, so it cannot overwrite the webinar by inherited ID.

The platform applies its environment-specific track naming rule during publish. Do not hard-code test suffixes into this course. Use Fieldkit’s normal test-to-live path; no resources have been created or modified in that platform repository.

The buildkit’s generic `DemoProject`, shared Temporal Cloud namespace and crashable Worker acceptance checks concern a different resource kind. This course needs no Worker or task-queue adapters. The applicable checks are the container build, per-guest/per-browser isolation, source/image binding and a real Instruqt learner play. Fieldkit’s current `operator/cmd/validate-projects` accepted the draft resource. Runtime checks remain pending because the authoring workspace could not access Docker.
