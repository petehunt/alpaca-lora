setup: .setup

.setup:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip
	git submodule update --init
	cd llama.cpp && make -j
	git lfs install
	touch .setup

dev:
	DAGSTER_HOME="$(shell pwd)/dagster_home" venv/bin/dagster dev -m alpaca_lora -h 0.0.0.0