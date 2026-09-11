.PHONY: test sanitize pdf

test:
	tools/test.sh

sanitize:
	SANITIZE=1 tools/test.sh

pdf:
	tools/build_pdf.sh

.PHONY: format format-check
format:
	tools/format.sh

format-check:
	tools/format.sh --check
