.PHONY: help install test clean run console docker-build docker-run package package-all

help:
	@echo "LLCAR Video Processing Pipeline - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install       - Install dependencies and setup environment"
	@echo "  test          - Run component tests"
	@echo "  clean         - Clean generated files and cache"
	@echo "  run           - Run the pipeline (set VIDEO=/path/to/video.mp4)"
	@echo "  console       - Launch interactive console mode"
	@echo "  package       - Build distributable package for current platform"
	@echo "  package-all   - Build distributable packages for all platforms"
	@echo "  docker-build  - Build Docker image"
	@echo "  docker-run    - Run in Docker (set VIDEO=/path/to/video.mp4)"
	@echo ""

install:
	@echo "Installing LLCAR..."
	@bash install.sh

test:
	@echo "Running tests..."
	@python3 test_pipeline.py

clean:
	@echo "Cleaning up..."
	@rm -rf __pycache__ src/__pycache__
	@rm -rf .pytest_cache
	@rm -rf build dist *.egg-info
	@find . -type f -name "*.pyc" -delete
	@echo "Clean complete"

run:
	@if [ -z "$(VIDEO)" ]; then \
		echo "Error: Please set VIDEO=/path/to/video.mp4"; \
		exit 1; \
	fi
	@python3 main.py --video $(VIDEO) $(ARGS)

console:
	@echo "Launching interactive console..."
	@python3 main.py --interactive

package:
	@echo "Building distributable package..."
	@python3 build_package.py

package-all:
	@echo "Building packages for all platforms..."
	@python3 build_package.py --all

docker-build:
	@echo "Building Docker image..."
	@docker build -t llcar .

docker-run:
	@if [ -z "$(VIDEO)" ]; then \
		echo "Error: Please set VIDEO=/path/to/video.mp4"; \
		exit 1; \
	fi
	@docker run -it \
		-e HF_TOKEN=${HF_TOKEN} \
		-v $(PWD)/input:/app/input \
		-v $(PWD)/output:/app/output \
		llcar --video $(VIDEO) $(ARGS)
