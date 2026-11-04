---
slug: launch-clearance
type: challenge
title: Ziggy's launch clearance
teaser: Everything is running. Can you see it?
tabs:
- title: Launchpad
  type: service
  hostname: workshop
  port: 5000
- title: Terminal
  type: terminal
  hostname: workshop
  cmd: /opt/preflight/bin/terminal.sh
- title: Editor
  type: service
  hostname: workshop
  port: 8080
  path: /?folder=/root/preflight
- title: Browser
  type: service
  hostname: workshop
  port: 8090
  path: /ziggy
- title: Temporal UI
  type: service
  hostname: workshop
  port: 8233
  path: /namespaces/default/workflows
difficulty: basic
timelimit: 900
---

# Ready when you are

Everything has started for you.

1. In **Launchpad**, look for Ziggy, the code editor and Temporal UI. Confirm each one you can see.
2. Open **Terminal** above. Look for **ZIGGY ONLINE** and a ticking clock.
3. Return to **Launchpad**, confirm the terminal, then click **Check** below.

That’s it. No commands or editing.

If a preview is small or blank, try its full-size tab above. A login page, spinner or error does not count as seeing the application.

## Something blocked?

Choose the issue button on that card. Launchpad shows help and a readiness report you can share with your webinar organizer.

If Launchpad itself is blank, tell your organizer **“Pre-flight Launchpad did not load”** and name your browser and whether you are using a work laptop or VPN. Your IT team can review the [Instruqt network requirements](https://docs.instruqt.com/reference/platform/third-party-network-access).

Keep company security controls enabled. Use only an IT-approved alternative setup.
