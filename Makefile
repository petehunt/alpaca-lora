setup:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip
	git submodule update --init
	cd llama.cpp && make -j
	git lfs install