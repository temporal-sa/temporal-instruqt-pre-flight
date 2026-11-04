COMPOSE ?= docker compose
.PHONY: demo test validate logs terminal reset down

demo:
	$(COMPOSE) up --build --detach --wait sandbox
	@echo "Launchpad: http://localhost:5000"
test:
	$(COMPOSE) run --rm --build test
validate:
	cd instruqt && instruqt track validate
logs:
	$(COMPOSE) exec sandbox bash -c 'tail -n 60 /run/preflight/*.log'
terminal:
	$(COMPOSE) exec sandbox /opt/preflight/bin/terminal.sh
reset:
	$(COMPOSE) down
	$(MAKE) demo
down:
	$(COMPOSE) down
