
all: site/content/churches opc.yaml site/content/churches/*.md
	python extract2.py

site/content/churches:
	mkdir -p site/content/churches


.PHONY: all