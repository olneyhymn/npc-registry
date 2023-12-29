
all: site/content/churches opc.yaml site/content/churches/*.md venv
	$(VENV)/python extract2.py

site/content/churches:
	mkdir -p site/content/churches

include Makefile.venv

.PHONY: all