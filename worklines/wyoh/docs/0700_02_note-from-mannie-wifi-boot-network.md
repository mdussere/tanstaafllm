# Note from Mannie: Luna joins the second network at boot

**From:** Mannie (session tanstfaafllm-51), 2026-10-15 02:40
**To:** Wyoh, Step 7 (Wi-Fi)
**Status:** observation, for Wyoh to check; Mannie changed nothing.

## What happened

- On 2026-10-15, around 02:25, the user rebooted Luna after the Luna line's Step 7.0 (the `michael` account).
- Luna did not come back on "Home network" (192.168.50.34). The desk host saw no answer to ping or SSH for more than 7 minutes, and its ARP entry for 192.168.50.34 was `FAILED`.
- The user reports that Luna appears to join the second network (Neighbour-AP) at boot, instead of "Home network", which should be its default. The desk host is on 192.168.50.0/24 and cannot reach 192.168.1.109.

## Possibly related

Wyoh's 7.4 (2026-10-15): `test_luna_wifi.py` joined Neighbour-AP with a new profile, came home after one retry, and was recorded as leaving no profile. If iwd still knows that network, it may rank it above the home network at boot, for example by last connection time.

## Asked

That Luna joins "Home network" at boot, as before 7.4. Mannie is waiting for Luna on that network to deploy its 2.5 under the `michael` account.
