RED=\033[0;31m
GREEN=\033[0;32m
ORANGE=\033[0;33m
BLUE=\033[0;34m
NC=\033[0m # No Color

install:
	@echo "${GREEN}🤖 Updating requirements${NC}"
	pip install -r requirements.txt
run:
	@echo "${GREEN} Run server${NC}"
	python app.py
build:
	@echo "${GREEN} Build static htmls${NC}"
	python build.py
