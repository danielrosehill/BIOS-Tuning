# IP-KVM backends: eyes and hands

An agent in firmware setup needs two things: **eyes** (a picture of the screen) and **hands** (keystrokes).
They can come from different routes. Pick per KVM:

| KVM | Eyes | Hands | Power / virtual media |
| --- | --- | --- | --- |
| Luckfox PicoKVM | Browser on the web UI (WebRTC; no HTTP snapshot). On-device `ffmpeg -f v4l2 -i /dev/video0` fails: `Not a video capture device` (rkcif multiplanar nodes held by the KVM app; tested 2026-11-17) | `ssh-hidg`: root SSH, write HID reports to `/dev/hidg0` (`scripts/hid-keys.py`). Browser typing also works | No ATX control without the Ext board. Virtual media in the web UI. Powered from the host's USB port: a host power-off can take the KVM down too |
| PiKVM / BliKVM (kvmd) | `GET /api/streamer/snapshot` returns a JPEG (headers `X-KVMD-User`, `X-KVMD-Passwd`), or the browser | `pikvm` backend: `POST /api/hid/events/send_key?key=<code>&state=true|false`; `POST /api/hid/print` for text | `POST /api/atx/click?button=power|power_long|reset` (with ATX board); `/api/msd/*` for virtual media |
| JetKVM | Browser (WebRTC) | Browser typing; the device has an optional developer-mode SSH but no documented HID-over-SSH path | Virtual media in the web UI |
| Sipeed NanoKVM | Browser, or its MJPEG stream (check the current API docs for the path and auth) | Browser typing | ATX control on the full variant; virtual media in the web UI |
| Anything else with a web console | Browser | Browser | Whatever the UI offers |

Claims about JetKVM and NanoKVM APIs are from vendor docs as remembered, not tested by this plugin: check them
against the device before relying on them, and update this table.

## Browser route (works for every KVM)

1. Open the KVM web UI in the browser the agent drives (Claude in Chrome, Playwright, or another browser MCP).
   Log in with the password from the user's secret store; never write it into a file.
2. Take a screenshot to read the screen. Zoom or crop when menu text is small: BIOS fonts at 1024x768 scaled
   into a browser window are easy to misread. Read values twice before acting on them.
3. To type through the browser, click once inside the video element to focus it, then send key presses.
   Some UIs need "keyboard capture" toggled or offer an on-screen keyboard; prefer the device's hands route
   from the table when there is one, because browser focus is easy to lose.
4. Keep the tab open the whole session. Re-opening a WebRTC session can take seconds and miss POST.

## Checks before any session

- KVM reachable on the network (ping, then the web UI loads a login page, not just HTTP 200: some KVM UIs
  answer 200 for every path).
- USB data link up. For gadget KVMs: `cat /sys/class/udc/*/state` on the KVM = `configured`. `not attached`
  or `default` means power-only cable or wrong port; keys will not reach the host.
- Video present: the screenshot shows the host's current screen, not "No signal".
- If the agent's own tools run on the machine being tuned (a gateway, an MCP server, a database), they go
  away at reboot. Install this plugin and any browser tooling locally on the machine driving the session
  first, and read the plan into the session before rebooting.
