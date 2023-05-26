setup: venv llama.cpp/main .git-lfs

venv:
	rm -fr .venv
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	ln -s .venv venv

llama.cpp/Makefile:
	git submodule update --init

llama.cpp/main: llama.cpp/Makefile
	cd llama.cpp && make -j

.git-lfs:
	git lfs install
	touch .git-lfs

mock_data.json: venv
	venv/bin/python3 alpaca_lora/utils/generate_fake_data.py

dev: setup
	mkdir -p "$(shell pwd)/dagster_home"
	DAGSTER_HOME="$(shell pwd)/dagster_home" venv/bin/dagster dev -m alpaca_lora -h 0.0.0.0
