---
slug: launch-clearance
type: challenge
title: Pre-flight check
teaser: Confirm you can access the hands-on lab content.
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

# Pre-flight check

Instruqt is the browser-based lab platform we use for the hands-on portion of the workshop. You will work in a code editor, terminal and the Temporal UI right in your browser, with nothing to install.

This pre-flight check confirms you can access the hands-on lab content from this computer, browser and network. If you cannot, we suggest joining from a personal machine rather than a work machine.

## What to do

1. Stay on the **Launchpad** tab at the top of the screen. It walks you through four short steps, one at a time.
2. In the **Terminal** step, Launchpad asks you to open the **Terminal** tab, look at it, and return to **Launchpad**.
3. When Launchpad shows your results, click **Check** below.

You do not need to install anything or type any commands.

## If something does not load

Answer "No" on that step. Launchpad shows what to try. Let your workshop organizer know what did not load. If Launchpad itself is blank, tell your organizer "The pre-flight Launchpad did not load" and name your browser, and whether you are on a work laptop or VPN.

Your IT team can review the [Instruqt network requirements](https://docs.instruqt.com/reference/platform/third-party-network-access).
