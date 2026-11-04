# Kit gaps

## Shared component CSS locks scrolling by default

`temporal-components.css` sets `html, body { height: 100%; }` and `body { overflow: hidden; }` globally for its booth layout. On the longer Launchpad page this hid the lower checks. Launchpad now explicitly uses normal document height and root scrolling, scoped to `.launchpad-page`. The kit should make its fixed viewport rules opt-in to `.app-shell`, so reusing buttons and disclosures cannot lock an unrelated page.

The Temporal demo buildkit supplied reusable theme, button, status, mascot and accessibility guidance. Its onboarding baseline currently points to the older `tmprl-demo-cloud-registry` and focuses on `DemoProject` Workers and Temporal Cloud. This project uses the owner’s newer `temporal-fieldkit-platform` `InstruqtCourse` contract and its per-guest container model. That is recorded in `catalog.md` and the README.

## Draft learning: sandbox health cannot prove browser readiness

A remote lab’s service can be healthy while a guest sees a blocked frame or frozen terminal. Instruqt’s documented network paths separate sandbox traffic from the guest’s HTTPS/WSS proxy connection; its automated track test exercises lifecycle scripts.

Use prepared real applications and a short visual confirmation to test what the guest can actually see. Keep sandbox health probes for setup diagnostics, and label an automatic WebSocket probe as connection evidence rather than a terminal-use test. A ready-made buildkit pattern for this distinction would help future pre-flight courses.

Evidence: official network and track-test references in `instruqt-research.md`. A managed-laptop learner play is still pending; no particular corporate product or policy has been identified as the cause of prior event issues.
