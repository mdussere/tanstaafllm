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

.PHONY: wyoh-luna-app wyoh-luna-apps wyoh-luna-deploy-preview wyoh-luna-deploy wyoh-luna-start wyoh-luna-stop wyoh-luna-status wyoh-luna-enable wyoh-luna-disable

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

.PHONY: help run-mike run-mike-rpg run-mike-rpg-fake run-camp-currie run-mannie

help:
	@echo "make run-mike           Mike in this terminal (MIKE_LANG=fr for French)"
	@echo "make run-mike-rpg       Mike in the RPG dialogue window (Wyoh 6.13, look B)"
	@echo "make run-mike-rpg-fake  the RPG window with a fake Mike (no model needed)"
	@echo "make run-camp-currie    the Camp Currie game (arrows, Return = A, Escape = B)"
	@echo "make run-mannie         Mannie: Claude Code in this repository"

run-mike:
	MIKE_HOME=$(MIKE_HOME) MIKE_LANG=$(MIKE_LANG) python3 $(MIKE_HOME)/mike.py

run-mike-rpg:
	MIKE_HOME=$(MIKE_HOME) MIKE_LANG=$(MIKE_LANG) uv run --group camp-currie python src/wyoh/apps/mike/mike_rpg.py

run-mike-rpg-fake:
	uv run --group camp-currie python src/wyoh/apps/mike/mike_rpg.py -- python3 test/wyoh/fixtures/fake_mike.py

run-camp-currie:
	cd src/camp-currie && uv run --group camp-currie python -m camp_currie

run-mannie:
	claude
