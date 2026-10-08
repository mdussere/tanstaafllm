# Getting a cheap handheld onto Wi-Fi with Linux — the R36 Ultra story

*September – October 2026*

This is the story of how we took an R36 Ultra, a small and inexpensive game handheld, and turned it into a little Linux computer we can reach over Wi-Fi from a PC. It's written to be read from top to bottom. The detailed technical records live in the project's `worklines/luna/docs/` folder; this page keeps to what happened and why.

---

## The starting point

The R36 Ultra looks like a toy: a square 720×720 screen, game buttons, a microSD card slot. Inside, though, it's a real ARM computer (a Rockchip RK3326) running Linux. It ships with a gaming system on a microSD card, and on that card everything works: screen, buttons, sound and Wi-Fi.

We didn't want a game console. We wanted a general-purpose Linux system on it that we could log into, install things on and build upon. So the plan was to put a different Linux system on a second microSD card and get it working as well as the original.

## Step 1 — Keep the original card safe

Before experimenting, we made a full copy of the original card. It's the only thing we knew worked perfectly on this exact device, so it was our reference and our way back.

That took two attempts. The first "copy" turned out to be a 62-byte file: the command that needed administrator rights had failed silently, and only its error message was saved. The second attempt used a small script that checks it has the right card, makes the card read-only, copies it, and then verifies that the copy is identical to the card, byte for byte. The original card then went into a drawer, untouched.

## Step 2 — Choosing a system

Several community Linux systems exist for this family of handhelds; the R36 Ultra is one of many "clones". We tried one that showed a picture but then kept restarting its interface in a loop, and we set it aside. We settled on **ArchR**, a system based on Arch Linux. It looked the most like a normal Linux system, and it already contained a driver for the handheld's Wi-Fi chip.

## Step 3 — A black screen, and why

The first ArchR card showed nothing at all. That turned out to be a missing step rather than a failure. These clones use many different screens, and ArchR needs a small description of the right one. Its official card-writing tool, *Arch R Flasher*, can generate that description from the original card's hardware description file, which we had saved. Once we used it, the screen came alive and ArchR started its game menu.

## Step 4 — Plugging a keyboard into a handheld

ArchR's menu showed that the network settings weren't usable, so we needed a proper terminal to see what was going on. A handheld has no keyboard, so we plugged one in.

- **The first try failed.** A wireless keyboard through a multi-port USB-C hub did nothing, not even its Caps Lock light. Hubs like that do a lot of negotiating, and small devices often don't cope.
- **The fix was a simple adapter.** A plain USB-C (male) to USB-A (female) adapter with only the keyboard's receiver plugged in worked straight away.

## Step 5 — Finding a terminal

On a normal Linux PC, **Ctrl + Alt + F2** switches from the graphical screen to a text login. On the handheld it switched to a **black screen**, and **Ctrl + Alt + F1** brought the menu back. So the keyboard worked, but there was no login waiting on that screen.

We took the card out and read it on the PC to understand why. ArchR has two start-up modes:

- the **normal mode**, which starts the graphical game menu;
- a **text mode**, which instead opens a ready-to-use administrator shell on the screen.

It simply doesn't offer a login screen on the other terminals, which explains the black screen. So we changed one line in the card's boot settings to make it start in text mode. On the next boot the handheld showed a command prompt.

One more annoyance: the keyboard behaved as if it were American (QWERTY), while ours is French (AZERTY). ArchR lacks the usual tools to change that, so we built the French layout on the PC and added a tiny step that loads it whenever the text shell starts. After that, typing on the handheld worked normally.

## Step 6 — Where is the Wi-Fi?

With a working terminal, we could finally look. Linux listed **no Wi-Fi interface at all**, only the internal "loopback" one. The Wi-Fi driver was on the card but not running.

Looking further down showed the real picture. The Wi-Fi chip sits on an internal connection that works much like an SD-card slot. Linux could see the slot, but nothing was in it: the chip was invisible.

## Step 7 — Reading the hardware description

On this kind of device, Linux can't discover how the board is wired. It reads it from a **hardware description file** (a "device tree") loaded at start-up. It says things like "this pin powers the Wi-Fi chip" or "this slot holds a removable SD card".

We compared the original card's description with the one ArchR uses, which is a generic one shared by many R36 clones. The difference was clear:

- the **original** said: *the slot holds the Wi-Fi chip, and pin 2 switches the chip on*;
- **ArchR's** said: *the slot is a second SD-card reader, and pin 2 tells us whether a card is inserted*.

So ArchR was **listening** on the wire it should have been **driving**. The chip was never switched on, which is why it was invisible.

## Step 8 — Three small corrections

ArchR lets you add small "patches" (overlays) on top of its hardware description without changing the system itself. We wrote one, tested it on the PC first, and added it to the card's boot settings with a script that keeps a backup. Each version got the hardware one step further:

1. **Switch the chip on.** The first patch drove pin 2 to power the chip and declared the slot as non-removable. The chip appeared, the driver loaded by itself, and its firmware was uploaded. But the firmware then failed to start, and only on some boots.
2. **Keep the clock running.** Reading ArchR's own source code, we found it has special handling for this Wi-Fi chip, but it only switches it on when the hardware description contains a particular marker. The original file had that marker; our patch didn't. With the marker added, the firmware started every time, and a Wi-Fi interface (`wlan0`) finally appeared.
3. **Connect the right "doorbell" wire.** The interface still refused to switch on. This chip notifies Linux of every event through a dedicated wake-up wire, and we had followed the driver's example board, which uses a different pin. The original description named another pin; with that one, Linux started receiving the chip's messages. The handheld could now scan and see our home network.

We had to take the card back to the PC between attempts, and many photos of the handheld's screen went back and forth along the way. But each attempt narrowed things down, and the error messages always pointed at the next layer.

## Step 9 — The router had a say

Now the handheld could see the network but couldn't log in to it. The graphical menu didn't help either: it spun for five minutes and then gave up.

The error message (*"AP is in CSA process, reject auth"*) meant that Linux believed the router was in the middle of changing channels, and politely refused to connect until it finished. Recent Linux versions do this, and some ASUS routers set to choose their channel automatically are known to trigger it indefinitely, even though Windows doesn't care.

The fix had nothing to do with the handheld. In the router's settings we changed the 2.4 GHz channel from **Auto** to a **fixed channel (11)**. The next attempt connected immediately, and the handheld received an address on the home network. 🎉

## Step 10 — Logging in from the PC

The last goal was to stop typing on a tiny screen and log in from the PC with SSH.

- **Setting a password was fiddly.** ArchR's small built-in `passwd` refused our quick, simple password at first. It didn't matter, because we wanted key-based login anyway.
- **We sent the PC's public key over the network.** The handheld listened for one incoming connection and saved what it received, and the PC sent its public key. Then we switched on the SSH service, and `ssh luna` from the PC opened a shell on the handheld.

## Step 11 — Surviving a reboot

The first reboot test revealed two more surprises, both with the same cause. ArchR keeps part of its working files in memory, and memory is wiped at every power-off:

- the handheld **forgot the Wi-Fi network** it had joined;
- it **created a new SSH identity** at every start, so the PC warned that "the remote host identification has changed", exactly what you'd see if someone were impersonating the device.

ArchR already had permanent folders meant for both, but hadn't connected them. Two tiny settings files on the card's storage partition now point the Wi-Fi service and the SSH service at those permanent folders. After another reboot, with nobody touching the handheld, it rejoined the Wi-Fi and the PC logged in without any warning. That's where we are today.

---

## Where things stand

- The handheld runs ArchR from a spare microSD card, starts in text mode, joins the home Wi-Fi on its own, and accepts SSH from the PC.
- The original card is archived, verified and untouched.
- Every change is small, documented and reversible: one boot setting, one keyboard step, one hardware patch and two settings files.

Still unknown or untested:

- how stable the Wi-Fi is over hours of use and large transfers (the driver's authors report occasional hiccups);
- whether the connection keeps working if the router goes back to automatic channel selection (probably not);
- Bluetooth, sound and the graphical side under this setup.

## What we'd tell someone starting the same journey

1. **Copy the original card first,** and check that the copy is real.
2. **Use a simple USB-C to USB-A adapter** for a keyboard, not a multi-port hub.
3. **If the screen is black, look for a text mode** before assuming nothing works.
4. **The original card is your map.** Its hardware description file held every answer: which pin powers the Wi-Fi, which pin wakes the system, and which marker the driver needs.
5. **Change one thing at a time and read the error messages:** each one pointed at the next problem.
6. **Not every problem is on the device.** The last obstacle was a router setting.
