
all: site/content/churches opc.yaml venv
	$(VENV)/python extract2.py

site/content/churches:
	mkdir -p site/content/churches

include Makefile.venv

.PHONY: all