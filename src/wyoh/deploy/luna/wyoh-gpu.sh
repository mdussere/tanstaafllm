#!/bin/sh
# Make ArchR's Mali GPU driver active before the Wyoh Sway session starts (Step 5.8).
#
# At boot, ArchR's `gpudriver --start` can run before mali_kbase can bind; it
# then falls back to panfrost (which also fails here) and removes the libmali
# bind mounts, leaving Sway in software rendering and the DSI panel black.
# So: retry mali_kbase until /dev/mali0 exists, then let ArchR's script set up
# its libmali bind mounts with the driver already bound.
# modprobe lives in /usr/sbin, which a unit PATH may lack (it did: Mali never
# loaded at boot and the error was hidden).
export PATH="/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
i=0
while [ ! -e /dev/mali0 ] && [ "$i" -lt 30 ]; do
    modprobe mali_kbase || echo "wyoh-gpu: modprobe mali_kbase failed (attempt $i)" >&2
    [ -e /dev/mali0 ] && break
    i=$((i + 1))
    sleep 1
done
if [ ! -e /dev/mali0 ]; then
    echo "wyoh-gpu: Mali GPU driver unavailable after 30 s; Sway will render in software" >&2
    exit 0
fi
if ! grep -q " /usr/lib/libEGL.so" /proc/mounts; then
    /usr/lib/archr/gpudriver --start
fi
echo "wyoh-gpu: Mali ready after ${i} retries"
exit 0
