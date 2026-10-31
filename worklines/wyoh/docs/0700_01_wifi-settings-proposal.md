# Proposal — choosing a Wi-Fi network from Luna's buttons

**Step:** Wyoh 7 (proposal; nothing is green-lit)
**Date:** 2026-10-09
**Question answered:** how a person joins, switches and forgets Wi-Fi networks on Luna without SSH, and who owns which part.
**Sources:**
- user request (2026-10-09): "my SSID and password are hard-coded; if I go to the office that won't work anymore" (from the [ChatGPT discussion](0500_02_input-widget-discussion-raw.md));
- user request: "add another step for the wifi config";
- Luna's Wi-Fi records (`worklines/luna/plan_luna.md` 5.8, `docs/0508_04`, `docs/0508_05`).

## 1. What Luna already has (Luna workline evidence)

| Fact | Source |
| --- | --- |
| ArchR manages Wi-Fi with **iwd**. Luna joined the home network with `iwctl`. | Luna 5.8g |
| iwd's saved networks persist in `/storage/.cache/iwd` (drop-in `iwd.service.d/10-persistent-state.conf`). | Luna 5.8i, `0508_05` |
| **ConnMan is also active**. In an earlier observation it saw only `lo`. Which one hands out addresses today is not recorded. | Luna 5.8a |
| A second profile file, `Home=20network.psk`, probably written by ArchR's settings UI, sits next to the one iwd uses. | `0508_05` |
| The home router needs a fixed 2.4 GHz channel (otherwise Linux 6.7+ refuses authentication with "AP is in CSA process"). Other access points may hit the same problem. | Luna 5.8f/g |

## 2. Ownership (cross-workline boundary)

| Part | Owner |
| --- | --- |
| The network stack: iwd, ConnMan, persistence, DHCP, drivers, firmware | **Luna**. Wyoh doesn't replace, reconfigure or disable it. |
| The screen and the button flow: list, choose, password, forget, status in the bar | **Wyoh** (this step) |
| Passwords | Kept only in iwd's own store on the card. Never in Git, logs, results or screenshots. |

If the read-only inventory (7.1) shows that iwd and ConnMan conflict, or that a stack change is needed, Wyoh writes a note to Luna and stops. It doesn't fix that itself.

## 3. Candidates

| Candidate | Verdict |
| --- | --- |
| iwgtk (graphical front-end for iwd) | **Rejected:** GTK, against the user's no-GTK decision |
| networkmanager-dmenu + fuzzel | **Rejected for now:** needs NetworkManager, which would replace iwd, a Luna stack change |
| nmtui / nm-sidebar / wifi-manager | Same NetworkManager dependency; nm-sidebar and wifi-manager also need GTK4 |
| `iwctl` in a terminal | Works today as a fallback for development, but it's not usable with buttons and its output is a coloured table, not an interface |
| **A Wyoh Wi-Fi panel on fuzzel + iwd's D-Bus interface** | **Recommended** |

## 4. Recommended design

- **The list** is a fuzzel menu, using the same look and the same buttons as the Start menu.
  - It's opened from the Start menu entry "Wi-Fi" (or FN+Select, to be decided).
  - Each line shows a mark for the current network, the SSID, the security type and the signal as bars: `✓ Home network  WPA2  ████`.
  - Below the networks: "Rescan", "Forget a network…" and "Disconnect".
- **Talking to iwd:** standard-library Python calls `busctl --json=short` (systemd's D-Bus tool, part of the base system) on `net.connman.iwd`: `Station.Scan`, `GetOrderedNetworks`, `Network.Connect`, `KnownNetwork.Forget`. No new Python dependency, no parsing of coloured text.
- **Known network:** `Connect` directly.
- **New WPA-PSK network:**
  1. Wyoh asks for the password: a masked Slate, typed with the on-screen keyboard (Step 6).
  2. It writes iwd's profile file itself (`<ssid>.psk`, `Passphrase=`, mode 600, iwd's filename encoding for unusual characters) into iwd's state directory.
  3. It calls `Connect`.

  This avoids registering a D-Bus password agent (`busctl` can't host one) and avoids putting the password on a command line.
- **Feedback:**
  - Success, failure (wrong password, authentication refused, no DHCP lease) and progress are shown honestly in a short pop-up.
  - The bar shows the SSID and the signal, via `status.sh`.
  - A failed new profile is removed, so a wrong password isn't kept.
- **Open networks:** connect without a password.
- **Not supported in v0:**
  - WPA-Enterprise / 802.1X: office networks often use it, and it needs certificates and identities. Proposed as a separate later step, once the office network's type is known.
  - Hidden SSIDs and captive portals: there is no browser.

## 5. Risks

- **Losing the development link:** Luna is driven over SSH on the same Wi-Fi. Mitigations:
  - live tests never forget the home network;
  - switch tests use a second access point (a phone hotspot) and then return home by themselves, checked from the local console if needed;
  - a USB keyboard and the tty1 console remain the recovery path.
- **iwd and ConnMan together:** which one owns `wlan0`'s addresses must be known before writing profiles (7.1, read-only).
- **Office access points** may hit the same CSA problem as the home router; Wyoh can only report the failure (the fix belongs to Luna or the router).
- **Filename encoding** of iwd profiles for SSIDs with spaces or special characters: follow iwd's documented rule and test it offline.

## 6. Tests

- **Deterministic:**
  - parsing `busctl` JSON into networks;
  - the menu text and ordering;
  - profile file content and name encoding (written into a temporary directory);
  - failure messages;
  - that no secret appears in any log line or status file.
- **Live** (`@pytest.mark.live`, Gherkin + pytest, MCP person, inspected screenshots):
  - open the panel and see the home network marked as connected;
  - rescan;
  - join a test access point with a dummy password, by buttons and on-screen keyboard;
  - a wrong password is refused, reported, and leaves no profile behind;
  - return to the home network.

  The test access point needs the user (it's a physical hotspot).
- **The user's check:** join the office network.

## 7. Decisions for the user

1. Confirm the design: a fuzzel-based panel on iwd, rather than switching to NetworkManager.
2. Entry point: the Start menu only, or also a button (FN+Select)?
3. Is the office network WPA2-Personal (password) or Enterprise (login + certificate)? This decides whether v0 is enough there.
4. Can a phone hotspot serve as the test access point?
