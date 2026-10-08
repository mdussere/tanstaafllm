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

.PHONY: wyoh-luna-deploy-preview wyoh-luna-deploy wyoh-luna-start wyoh-luna-stop wyoh-luna-status wyoh-luna-enable wyoh-luna-disable

wyoh-luna-deploy-preview:
	rsync -e "$(WYOH_LUNA_SSH)" --archive --no-owner --no-group --checksum --dry-run --itemize-changes --mkpath --exclude '__pycache__/' src/wyoh/ $(WYOH_LUNA_HOST):$(WYOH_LUNA_ROOT)/
	rsync -e "$(WYOH_LUNA_SSH)" --archive --no-owner --no-group --checksum --dry-run --itemize-changes --mkpath src/wyoh/deploy/luna/wyoh-sway.service $(WYOH_LUNA_HOST):$(WYOH_LUNA_UNIT)

wyoh-luna-deploy:
	rsync -e "$(WYOH_LUNA_SSH)" --archive --no-owner --no-group --checksum --mkpath --exclude '__pycache__/' src/wyoh/ $(WYOH_LUNA_HOST):$(WYOH_LUNA_ROOT)/
	rsync -e "$(WYOH_LUNA_SSH)" --archive --no-owner --no-group --checksum --mkpath src/wyoh/deploy/luna/wyoh-sway.service $(WYOH_LUNA_HOST):$(WYOH_LUNA_UNIT)
	rsync -e "$(WYOH_LUNA_SSH)" --archive --no-owner --no-group --checksum --mkpath src/wyoh/deploy/luna/wyoh-gamepad.service $(WYOH_LUNA_HOST):$(WYOH_LUNA_GAMEPAD_UNIT)
	rsync -e "$(WYOH_LUNA_SSH)" --archive --no-owner --no-group --checksum --mkpath src/wyoh/deploy/luna/wyoh-layout.service $(WYOH_LUNA_HOST):$(WYOH_LUNA_LAYOUT_UNIT)
	$(WYOH_LUNA_SSH) $(WYOH_LUNA_HOST) 'systemctl daemon-reload'

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
