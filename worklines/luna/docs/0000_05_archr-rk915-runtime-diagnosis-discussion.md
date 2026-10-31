# R36 Ultra — preserve the hardware reference, then stage an alternative-base trial

> **Freshness:** 🟡 historical · **Written:** 2026-10-04 · **Checked:** 2026-10-31

## Summary

The discussion moves the immediate priority from further Arch-R Wi-Fi debugging to protecting the factory EmuELEC card: it is the only verified hardware reference for this particular R36 Ultra. It then proposes a controlled dArkOSRE trial on a separate card, because it was reported to have beta R36 Ultra support and a more conventional Debian userspace.

Nothing in this discussion proves dArkOSRE compatibility, its current release status, or a particular DTB procedure. The next work must verify those claims from official release material and must never alter the factory card.

## Detailed summary

**Keyboard and console access**

- The connected 2.4 GHz keyboard/dongle did not react through a multi-port USB-C hub; its Caps Lock LED works on the PC but not on the handheld.
- The conversation infers that the hub/OTG chain is the immediate blocker, not an F-key shortcut. A simple USB-C-to-USB-A OTG adapter is the next physical diagnostic.
- Once keyboard access works, a TTY and runtime evidence can distinguish missing module activation, DTB/MMC configuration, and firmware failure from a missing driver.

**What the mounted-image evidence changes**

- The conversation correctly shifts from “the driver is absent” to “the driver may not be loaded or bound.” The subsequent Luna evidence confirms that Arch-R already contains the matching RK915 module and firmware.
- A future Arch-R runtime record should cover the active DTB, overlay activation, module state, SDIO binding, and kernel log before any modification.

**Factory EmuELEC as the hardware reference**

- The delivered EmuELEC image has proven boot, display, controls, audio, and Wi-Fi on this device. It should be imaged and stored before experimentation.
- It is an appliance-style system, so removing its gaming stack in place is not assumed to be a viable general-purpose Linux route.
- Its bootloader, kernel, DTB, modules, and firmware remain valuable BSP evidence even if a later userspace is chosen.

**Alternative-base proposal**

- The discussion proposes dArkOSRE as the first alternate image to test, ahead of spending further time repairing Arch-R, because it was reported to target the R36 Ultra in beta and to use a Debian-family userspace.
- The trial criterion is deliberately narrow: boot, screen, controls, internal Wi-Fi, and SSH—not gaming performance or installing a desktop stack.
- The image-supplied R36 Ultra DTB must be identified from official release material and used first. The factory DTB is a reference for later comparison, not an automatic replacement.

**Safety boundary**

- `golden/` holds the compressed factory-card image, checksum, and extracted DTB; it is immutable.
- Downloaded release artifacts are retained with URL, version, date, and checksum; all experimental writes target a separately identified disposable card.
- Flashing, first boot, Wi-Fi configuration, and any working-card change remain pending a separate green light.

## Cleaned verbatim

> Translated from a French ChatGPT discussion captured on 2026-09-27. Editorial section headings were added for readability. “Arch Air” and “Archer” in the original speech are rendered as Arch-R (likely speech-recognition variants); “dArkOSRE” retains the project’s stylisation. Assistant technical and support claims are preserved as discussion claims, not independently verified facts.

### § 1. The keyboard does not yet provide console access

**User:** I tried connecting a keyboard to the console with Arch-R installed, but I cannot get to console mode. I am on the main screen and tried F5 with the connected keyboard, but I cannot make it work.

**Assistant:** F5 does not appear to be the right route. The discussion proposes trying the standard Linux shortcuts `Ctrl+Alt+F2`, then F3 through F6. If a black `login:` screen appears, the earlier assistant claimed the published default credentials were `archr` / `archr`. If none of those shortcuts changes anything, it suggests that no getty is active on the virtual terminals or that EmulationStation/KMS owns the console; the card could then be inspected from Termidor rather than guessing more shortcuts.

**User:** Nothing changes. Is there a way to tell whether my keyboard is active?

**Assistant:** First try arrows, Enter, Escape, and Space in the Arch-R/EmulationStation interface. If selection moves, Linux sees the keyboard and only console access is blocked. Caps Lock or Num Lock LEDs can at least show power/controller activity, although they are not complete proof. `Ctrl+Alt+Delete` might reboot the device, so it should only be used if a reboot is acceptable. If no keys or LEDs react, the OTG/data port and connection chain need checking.

### § 2. The wireless keyboard and hub are the immediate uncertainty

**User:** The keyboard is wireless and has a USB dongle; could that be the issue? It is plugged into the port labelled OTG.

**Assistant:** A 2.4 GHz keyboard dongle normally appears to Linux as a USB HID keyboard without a special driver. However, the path here is USB-C OTG, adapter, radio dongle, and keyboard; power, OTG negotiation, or handheld USB support can each fail. A basic wired USB keyboard through OTG would remove the radio, pairing, battery, and dongle variables. A wired mouse could also provide a coarse OTG test.

**User:** I meant a normal wireless keyboard with a USB dongle. Caps Lock does not light when it is connected to the console, though it lights when connected to my computer. I used a USB-C multi-port hub because I did not have the correct adapter; perhaps that is too demanding for the small console.

**Assistant:** The comparison is a strong indication that the keyboard/dongle works but the R36 Ultra does not communicate with it through the hub. The earlier assistant suspects USB-C/OTG negotiation as much as power draw: complex hubs can expose HDMI, readers, Ethernet, or Power Delivery behaviours that small ARM devices tolerate poorly. The proposed clean test is a simple USB-C male-to-USB-A female OTG adapter with only the keyboard dongle attached. Continuing to try TTY shortcuts before that test is not useful.

**User:** I ordered a USB-C-to-USB-A adapter and will try again in a day or two.

**Assistant:** The proposed order is Caps Lock first, then arrows/Enter in the interface, then `Ctrl+Alt+F2/F3/F4`. Meanwhile, card inspection can continue without the console.

### § 3. A present driver does not prove a live Wi-Fi binding

**User:** I mounted the microSD and checked it. The necessary drivers are already in Arch-R. We verified that the EmuELEC driver used by the supplied hardware covers the same Wi-Fi connector. It should work, but it does not.

**Assistant:** The key distinction is between a driver being present on disk and being loaded and bound to the hardware. Once console access is available, the discussion proposes checking the network devices, loaded modules, `dmesg`, `iw dev`, and firmware messages. A working path may still fail as `hardware → SDIO → driver on disk → no wlan0` if the DTB does not expose the chip, a module never loads, or firmware initialisation fails. Because Arch-R did not explicitly expose the exact Ultra model in the reported flasher flow, the discussion identifies the DTB as a leading hypothesis.

### § 4. EmuELEC is a valuable BSP reference, not automatically the final userspace

**User:** Could we use the EmuELEC supplied with the console? It works over SSH. Could we duplicate it, remove what we do not need, and then install window managers and so on?

**Assistant:** The supplied EmuELEC image is described as a “golden image” because it boots on this hardware with display, controls, audio, and Wi-Fi working. The discussion warns that it is an appliance-oriented, largely immutable build rather than a general mutable distribution; it is not assumed that one can simply remove EmulationStation and install Sway.

The proposed architectural separation is to preserve the known-working BSP—bootloader, kernel, exact DTB, kernel modules, Wi-Fi firmware, display configuration, controls, and audio—while replacing userspace progressively. A hypothetical minimal Luna rootfs alongside the existing system would start from kernel/network/SSH, then Wayland, Sway, Wyoh, Mycroft, and Mike. The discussion says this needs later verification of dependencies, redistribution/licensing, and whether the vendor kernel expects a particular userspace.

**User:** Would that mean cross-compiling everything? Arch-R already has Sway.

**Assistant:** The discussion contrasts Arch-R’s general-purpose Arch ARM userspace, where packaged components may be installed directly, with EmuELEC’s image-build model. It suggests that retaining the working BSP while providing a normal ARM64 rootfs—Debian, Arch ARM, Alpine, or a Buildroot-built system—would not necessarily require building every component by hand. It frames Arch-R as a fast prototype candidate, EmuELEC as hardware truth, and Buildroot as a possible later production path; these are proposals, not decisions.

### § 5. Candidate distributions and the proposed dArkOSRE proof

**User:** We have concentrated on Arch-R and EmuELEC. What other distributions were on the list?

**Assistant:** The earlier assistant listed ROCKNIX, ArkOS, dArkOS/dArkOSRE, AmberELEC, ArkOS4Clone, NixOS R36S, Buildroot R36S, and a custom Debian/Ubuntu rootfs as possible references or bases. It singled out dArkOSRE as potentially interesting because it was said to be Debian Trixie-based and R36-oriented.

**User:** Would it be worth trying ArkOS or dArkOS to see whether one works cleanly by chance?

**Assistant:** The discussion recommends a dArkOSRE trial first, based on unverified claims that the latest beta explicitly supports an R36 Ultra board variant. Its proposed test is limited to a dedicated microSD and the sequence boot → screen → controls → Wi-Fi → SSH. It argues that this is worth doing before spending more days on Arch-R, but release availability, exact image, and support status must be checked from official sources when the step is green-lit.

### § 6. DTB selection, flashing, and reference preservation

**User:** How is dArkOSRE installed, and can the beta be obtained directly? I do not understand “select the DTB before first boot.” I have the DTB extracted from the working machine; how is it selected?

**Assistant:** The earlier assistant says DTB selection is a file operation on the flashed card’s BOOT partition, not a menu. It advises using the image’s supplied R36 Ultra DTB/configuration first, rather than immediately substituting the extracted factory EmuELEC DTB. The exact filenames and location must be read from the released image and its official instructions; no names should be guessed. The factory DTB is retained as a later comparison reference.

**User:** Do I need Raspberry Pi Imager, or can I use `dd`? I also want a small image archive: keep the factory image safe, retain downloaded candidate images, and experiment only on copies.

**Assistant:** The discussion says a command-line image write is technically suitable if the target device is identified with extreme care, but this is destructive and must never target the factory card. It proposes a separate image archive containing a compressed full-card factory copy, checksum, extracted factory DTB, original downloaded artifacts, their source URLs/versions/dates/checksums, and a separate working area. The governing distinction is: `golden/` is immutable, downloaded originals are retained unchanged, and only a separately verified working card may be written.

**User:** Is Zstandard compression?

**Assistant:** Yes. The discussion explains that zstd can compress a streamed block-level image without first storing an uncompressed card-sized file, and can decompress a stored image directly to a different card. It presents this as an archival technique, not as an instruction to write or alter the factory media now.
