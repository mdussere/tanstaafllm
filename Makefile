WYOH_HOST ?= luna-pi
WYOH_REMOTE_ROOT ?= /home/michael/.local/share/tanstfaafllm/wyoh
WYOH_UNIT ?= /home/michael/.config/systemd/user/wyoh-sway-vnc.service

.PHONY: wyoh-deploy-preview wyoh-deploy wyoh-activate wyoh-rollback wyoh-status

wyoh-deploy-preview:
	rsync --archive --checksum --dry-run --mkpath --exclude '__pycache__/' src/wyoh/ $(WYOH_HOST):$(WYOH_REMOTE_ROOT)/
	rsync --archive --checksum --dry-run --mkpath src/wyoh/deploy/luna-pi/wyoh-sway-vnc.service $(WYOH_HOST):$(WYOH_UNIT)

wyoh-deploy:
	rsync --archive --checksum --mkpath --exclude '__pycache__/' src/wyoh/ $(WYOH_HOST):$(WYOH_REMOTE_ROOT)/
	rsync --archive --checksum --mkpath src/wyoh/deploy/luna-pi/wyoh-sway-vnc.service $(WYOH_HOST):$(WYOH_UNIT)
	ssh $(WYOH_HOST) 'systemctl --user daemon-reload'

wyoh-activate: wyoh-deploy
	ssh $(WYOH_HOST) 'systemctl --user stop luna-vnc.service && systemctl --user disable luna-vnc.service && systemctl --user enable --now wyoh-sway-vnc.service'

wyoh-rollback:
	ssh $(WYOH_HOST) 'systemctl --user stop wyoh-sway-vnc.service && systemctl --user disable wyoh-sway-vnc.service && systemctl --user enable --now luna-vnc.service'

wyoh-status:
	ssh $(WYOH_HOST) 'systemctl --user --no-pager status wyoh-sway-vnc.service luna-vnc.service'

# Luna (ArchR, root over SSH). The Wyoh unit is not enabled at boot.
WYOH_LUNA_HOST ?= luna
# Luna's OpenSSH 9.8 penalises bursts of new connections (PerSourcePenalties);
# override with a multiplexed ssh, e.g. WYOH_LUNA_SSH='ssh -o ControlMaster=auto ...'.
WYOH_LUNA_SSH ?= ssh
WYOH_LUNA_ROOT ?= /storage/.local/share/tanstfaafllm/wyoh
WYOH_LUNA_UNIT ?= /storage/.config/system.d/wyoh-sway.service
WYOH_LUNA_GAMEPAD_UNIT ?= /storage/.config/system.d/wyoh-gamepad.service
WYOH_LUNA_LAYOUT_UNIT ?= /storage/.config/system.d/wyoh-layout.service

.PHONY: install install-wyoh luna-stop-all install-preview status wyoh-luna-app wyoh-luna-apps wyoh-luna-deploy-preview wyoh-luna-deploy wyoh-luna-start wyoh-luna-stop wyoh-luna-status wyoh-luna-enable wyoh-luna-disable

wyoh-luna-deploy-preview:
	rsync -e "$(WYOH_LUNA_SSH)" --archive --no-owner --no-group --checksum --dry-run --itemize-changes --mkpath --exclude '__pycache__/' src/wyoh/ $(WYOH_LUNA_HOST):$(WYOH_LUNA_ROOT)/
	rsync -e "$(WYOH_LUNA_SSH)" --archive --no-owner --no-group --checksum --dry-run --itemize-changes --mkpath src/wyoh/deploy/luna/wyoh-sway.service $(WYOH_LUNA_HOST):$(WYOH_LUNA_UNIT)

wyoh-luna-deploy:
	rsync -e "$(WYOH_LUNA_SSH)" --archive --no-owner --no-group --checksum --mkpath --exclude '__pycache__/' src/wyoh/ $(WYOH_LUNA_HOST):$(WYOH_LUNA_ROOT)/
	rsync -e "$(WYOH_LUNA_SSH)" --archive --no-owner --no-group --checksum --mkpath src/wyoh/deploy/luna/wyoh-sway.service $(WYOH_LUNA_HOST):$(WYOH_LUNA_UNIT)
	rsync -e "$(WYOH_LUNA_SSH)" --archive --no-owner --no-group --checksum --mkpath src/wyoh/deploy/luna/wyoh-gamepad.service $(WYOH_LUNA_HOST):$(WYOH_LUNA_GAMEPAD_UNIT)
	rsync -e "$(WYOH_LUNA_SSH)" --archive --no-owner --no-group --checksum --mkpath src/wyoh/deploy/luna/wyoh-layout.service $(WYOH_LUNA_HOST):$(WYOH_LUNA_LAYOUT_UNIT)
	$(WYOH_LUNA_SSH) $(WYOH_LUNA_HOST) 'mkdir -p $(WYOH_LUNA_ROOT)/generated && touch $(WYOH_LUNA_ROOT)/generated/sway-apps.conf && systemctl daemon-reload'

# One assembled app directory (Step 9) to /storage/.local/opt/<name>/ on Luna, e.g.
#   make wyoh-luna-app APP_DIR=results/wyoh/wolf3d-build/<ts> APP_NAME=wolf3d-ecwolf
wyoh-luna-app:
	test -n "$(APP_DIR)" && test -n "$(APP_NAME)" && test -f "$(APP_DIR)/wyoh-app.toml"
	rsync -e "$(WYOH_LUNA_SSH)" --archive --no-owner --no-group --checksum --mkpath --delete $(APP_DIR)/ $(WYOH_LUNA_HOST):/storage/.local/opt/$(APP_NAME)/

# Applications (Step 9.2/9.4): generate menu entries, hidden ArchR entries, Sway
# rules and gamepad profiles from every wyoh-app.toml on Luna, then reload.
WYOH_LUNA_APPS ?= --apps '/storage/.local/opt/*/wyoh-app.toml' --apps '$(WYOH_LUNA_ROOT)/apps/*/wyoh-app.toml'
wyoh-luna-apps: wyoh-luna-deploy
	$(WYOH_LUNA_SSH) $(WYOH_LUNA_HOST) "python3 $(WYOH_LUNA_ROOT)/wyoh_apps.py $(WYOH_LUNA_APPS) --menu $(WYOH_LUNA_ROOT)/deploy/luna/menu.toml --applications-dir $(WYOH_LUNA_ROOT)/deploy/luna/share/applications --out-dir $(WYOH_LUNA_ROOT)/generated --system-dir /usr/share/applications --system-dir /usr/local/share/applications; swaymsg -s \$$(python3 -c 'import json;print(json.load(open(\"/storage/.local/state/tanstfaafllm/wyoh/sway-vnc-session.json\"))[\"sway_socket\"])') reload >/dev/null; systemctl restart wyoh-gamepad.service"

# --- Install on Luna from the desk (Adam, 2026-11-03; shape agreed with Professor) ---
# `make install` rsyncs each workline's part from this working tree to Luna: no push
# or pull is needed. It TOUCHES LUNA: run it only with Mannie stopped on Luna, or with
# Mannie's agreement. No reboot; only a part's own service restarts; no model weights.
# `install` is an umbrella: each workline owns its target (install-wyoh now; Mike,
# Mannie and Camp Currie add theirs). A stamp on Luna records what was installed;
# `make status` prints it next to the desk's HEAD.
LUNA_STAMP ?= /storage/.local/state/tanstfaafllm/deployed.txt

install: install-wyoh
	$(WYOH_LUNA_SSH) $(WYOH_LUNA_HOST) 'mkdir -p $(dir $(LUNA_STAMP)) && echo "$(shell git describe --always --dirty) $(shell date -Iseconds) from $(shell hostname)" > $(LUNA_STAMP)'

# Adam, 2026-11-03: "when we reinstall, kill everyone, Mannie included, whatever its
# state. What comes back is Wyoh and Mycroft; everything else stays off." So
# luna-stop-all runs first: every window closes (Mike's too, so mike.py stops its
# server), Mannie's tmux session and claude end, any Mike or llama-server left is
# killed. Then Wyoh is installed and only Wyoh's services restart; Mycroft comes
# back with them (wyoh-gamepad loads its resident dictation). Patterns are bracketed
# so pkill never matches its own ssh command. Mannie's boot service is not changed.
SWAY_SOCK_CMD = python3 -c 'import json;print(json.load(open(\"/storage/.local/state/tanstfaafllm/wyoh/sway-vnc-session.json\"))[\"sway_socket\"])'

luna-stop-all:
	$(WYOH_LUNA_SSH) $(WYOH_LUNA_HOST) "swaymsg -s \$$($(SWAY_SOCK_CMD)) '[all] kill' >/dev/null 2>&1; runuser -u michael -- tmux kill-session -t mannie 2>/dev/null; sleep 3; pkill -x claude; pkill -f '[m]ike_rpg.py'; pkill -f '[m]ike.py'; pkill -f '[l]lama-server'; pkill -f 'MIKE_[H]OME'; pkill -f 'wyoh_[s]late.py'; pkill -f 'deploy/luna/[s]tatus.sh'; pkill -f '[d]ictation-indicator.sh'; sleep 1; pgrep -a -f '[c]laude|[l]lama-server|[m]ike.py' || echo 'all stopped'"

install-wyoh: luna-stop-all wyoh-luna-apps
	$(WYOH_LUNA_SSH) $(WYOH_LUNA_HOST) "systemctl restart wyoh-layout.service wyoh-gamepad.service; swaymsg -s \$$($(SWAY_SOCK_CMD)) reload >/dev/null; echo 'Wyoh and Mycroft restarted'"

install-preview: wyoh-luna-deploy-preview

status:
	@echo "desk HEAD:  $$(git describe --always --dirty)"
	@echo "on Luna:    $$($(WYOH_LUNA_SSH) $(WYOH_LUNA_HOST) 'cat $(LUNA_STAMP) 2>/dev/null || echo nothing installed by make install yet')"

wyoh-luna-start: wyoh-luna-deploy
	$(WYOH_LUNA_SSH) $(WYOH_LUNA_HOST) 'systemctl start wyoh-sway.service wyoh-gamepad.service wyoh-layout.service'

wyoh-luna-stop:
	$(WYOH_LUNA_SSH) $(WYOH_LUNA_HOST) 'systemctl stop wyoh-layout.service wyoh-gamepad.service wyoh-sway.service'

wyoh-luna-status:
	$(WYOH_LUNA_SSH) $(WYOH_LUNA_HOST) 'systemctl --no-pager status wyoh-sway.service wyoh-gamepad.service wyoh-layout.service sway.service essway.service seatd.service'

# Boot into the Wyoh session (Step 5.8): links under /storage/.config/system.d,
# the same mechanism the Luna workline uses for /home. The boot partition is not touched.
wyoh-luna-enable: wyoh-luna-deploy
	$(WYOH_LUNA_SSH) $(WYOH_LUNA_HOST) 'cd /storage/.config/system.d && mkdir -p textmode.target.wants wyoh-sway.service.wants && ln -sfn ../wyoh-sway.service textmode.target.wants/wyoh-sway.service && ln -sfn ../wyoh-gamepad.service wyoh-sway.service.wants/wyoh-gamepad.service && ln -sfn ../wyoh-layout.service wyoh-sway.service.wants/wyoh-layout.service && systemctl daemon-reload'

wyoh-luna-disable:
	$(WYOH_LUNA_SSH) $(WYOH_LUNA_HOST) 'cd /storage/.config/system.d && rm -f textmode.target.wants/wyoh-sway.service wyoh-sway.service.wants/wyoh-gamepad.service wyoh-sway.service.wants/wyoh-layout.service && rmdir --ignore-fail-on-non-empty textmode.target.wants wyoh-sway.service.wants && systemctl daemon-reload'

# --- Run the cell's programs on the desk (Termidor) --------------------------
# Adam, 2026-11-03: "make targets to launch things: run Mike, run Mannie, etc."
# Mike runs from MIKE_HOME (~/.local/opt/mike: mike.py, llama-b11429/, the model).
MIKE_HOME ?= $(HOME)/.local/opt/mike
MIKE_LANG ?= en
# Dictation in Mike's RPG window (F1/F2, or L1/L2 on a pad): Mycroft's resident English model, desk microphone.
MYCROFT_ASSETS ?= /data/michael/tanstaafllm/mycroft-assets
MIKE_MIC ?= /dev/snd/pcmC0D0c
MIKE_RPG_DICTATE ?= python3 $(CURDIR)/worklines/mycroft/scripts/mycroft_dictate.py --resident --model kroko-en-2025 --assets $(MYCROFT_ASSETS) --input $(MIKE_MIC)

.PHONY: help run-mike run-mike-rpg run-mike-rpg-fake run-camp-currie run-mannie

help:
	@echo "make run-mike           Mike in this terminal (MIKE_LANG=fr for French)"
	@echo "make run-mike-rpg       Mike in the RPG dialogue window (Wyoh 6.13, look B); F1/F2 or L1/L2 dictate, again to send"
	@echo "make run-mike-rpg-fake  the RPG window with a fake Mike (no model needed)"
	@echo "make run-camp-currie    the Camp Currie game (arrows, Return = A, Escape = B)"
	@echo "make run-mannie         Mannie: Claude Code in this repository"
	@echo "make install            install every workline's part on Luna from this tree (Mannie stopped or agreeing)"
	@echo "make install-preview    what make install would change on Luna (dry run)"
	@echo "make status             desk HEAD next to what is installed on Luna"

run-mike:
	MIKE_HOME=$(MIKE_HOME) MIKE_LANG=$(MIKE_LANG) python3 $(MIKE_HOME)/mike.py

run-mike-rpg:
	MIKE_HOME=$(MIKE_HOME) MIKE_LANG=$(MIKE_LANG) MIKE_RPG_DICTATE="$(MIKE_RPG_DICTATE)" uv run --group camp-currie python src/wyoh/apps/mike/mike_rpg.py

run-mike-rpg-fake:
	MIKE_RPG_DICTATE="$(MIKE_RPG_DICTATE)" uv run --group camp-currie python src/wyoh/apps/mike/mike_rpg.py -- python3 test/wyoh/fixtures/fake_mike.py

run-camp-currie:
	cd src/camp-currie && uv run --group camp-currie python -m camp_currie

run-mannie:
	claude
