# Step 4 recheck — Luna stock-inventory reachability

> **Freshness:** 🟡 historical · **Written:** 2026-09-27 · **Checked:** 2026-10-31 · **Step:** wyoh 4.5 ✅

**Status:** live recheck could not reach Luna; no target operation occurred, 2026-09-27.

## Question answered

Could the preserved Luna stock image be reached again to continue its read-only Step 4 inventory?

## Method

The existing pytest-owned live inventory was run through the configured `luna` SSH entry, with its per-test timeout set to 90 seconds and an outer 120-second process timeout. It retained the normal result directory under `results/wyoh/luna-stock-inventory/` and the complete runner log under `logs/wyoh/`.

No command reached a remote shell. The SSH connection failed before the inventory script could execute.

## Observed result

The test failed after 14.39 seconds with:

```text
ssh: connect to host 192.168.50.227 port 22: No route to host
```

This is a connectivity observation, not a change in the previous stock-image facts. In particular, it does not invalidate the successful 2026-09-27 EmuELEC/EmulationStation baseline in `0405_01_luna-stock-image-inventory.md`; it establishes only that the target was unreachable at this recheck.

## Consequence for Step 4

The missing visible-display and input evidence remains missing. Wyoh cannot safely claim controller mapping, overlays, launch/return behaviour, display-stack behaviour, or a Sway comparison while the target is unreachable and the stock card must remain untouched.

Keep the production-base outcome as **defer**. When the route is restored, rerun the same read-only inventory first, then obtain an explicit visual/input observation before considering any experiment on a separate card.
