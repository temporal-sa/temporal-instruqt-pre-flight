# The guest sees what will work before the webinar

A guest opens a prepared Instruqt sandbox and confirms that Ziggy, the editor, live terminal output and Temporal UI are visible from the laptop they will use for the webinar.

The guest spends a few seconds checking prepared screens. The course supplies the running services and a small automatic WebSocket check; it does not teach Temporal or ask the guest to run an exercise.

| Problem | Visible sign | Resolution and proof |
| --- | --- | --- |
| Corporate browser or network policy blocks a lab surface | A blank page, loading spinner or frozen terminal clock | A specific issue choice and help; the guest checks the same surface again after an IT-approved fix. |
| The organizer discovers the issue during the webinar | The guest cannot confirm one of the prepared screens | A short report can be shared before the webinar. Completion requires all four visual confirmations and a browser WebSocket round trip. |
| A sandbox-side probe gives false confidence about the guest’s browser | Services can be running while the guest still sees nothing | Browser previews and an actual Instruqt terminal, confirmed by the guest; iframe load events and sandbox HTTP success never become visual passes. |

The owner chose Ziggy’s launch clearance and then narrowed the experience to automatic startup and quick visual confirmations, with a container sandbox for Fieldkit. No local developer-tool setup is in scope.
