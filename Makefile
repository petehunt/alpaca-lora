setup: .setup

.setup:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt
	git submodule update --init
	cd llama.cpp && make -j
	git lfs install
	touch .setup

dev: setup
	DAGSTER_HOME="$(shell pwd)/dagster_home" venv/bin/dagster dev -m alpaca_lora -h 0.0.0.0