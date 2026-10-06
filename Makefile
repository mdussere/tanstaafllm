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
WYOH_LUNA_ROOT ?= /storage/.local/share/tanstfaafllm/wyoh
WYOH_LUNA_UNIT ?= /storage/.config/system.d/wyoh-sway.service

.PHONY: wyoh-luna-deploy-preview wyoh-luna-deploy wyoh-luna-start wyoh-luna-stop wyoh-luna-status

wyoh-luna-deploy-preview:
	rsync --archive --no-owner --no-group --checksum --dry-run --itemize-changes --mkpath --exclude '__pycache__/' src/wyoh/ $(WYOH_LUNA_HOST):$(WYOH_LUNA_ROOT)/
	rsync --archive --no-owner --no-group --checksum --dry-run --itemize-changes --mkpath src/wyoh/deploy/luna/wyoh-sway.service $(WYOH_LUNA_HOST):$(WYOH_LUNA_UNIT)

wyoh-luna-deploy:
	rsync --archive --no-owner --no-group --checksum --mkpath --exclude '__pycache__/' src/wyoh/ $(WYOH_LUNA_HOST):$(WYOH_LUNA_ROOT)/
	rsync --archive --no-owner --no-group --checksum --mkpath src/wyoh/deploy/luna/wyoh-sway.service $(WYOH_LUNA_HOST):$(WYOH_LUNA_UNIT)
	ssh $(WYOH_LUNA_HOST) 'systemctl daemon-reload'

wyoh-luna-start: wyoh-luna-deploy
	ssh $(WYOH_LUNA_HOST) 'systemctl start wyoh-sway.service'

wyoh-luna-stop:
	ssh $(WYOH_LUNA_HOST) 'systemctl stop wyoh-sway.service'

wyoh-luna-status:
	ssh $(WYOH_LUNA_HOST) 'systemctl --no-pager status wyoh-sway.service sway.service essway.service seatd.service'
