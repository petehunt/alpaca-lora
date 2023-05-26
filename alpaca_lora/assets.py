from dagster import asset, Config
from .utils.finetune import FinetuneConfig, finetune_alpaca_lora_model
from .utils.checkpoints import ExportCheckpointConfig, export_alpaca_lora_checkpoint
from .resources import DataDirectory
from pathlib import Path
import requests
from subprocess import run
import sys
import json

# TODO: convert from original llama weights?


class FoundationModelWeightsConfig(Config):
    huggingface_repo: str = "decapoda-research/llama-7b-hf"


@asset
def foundation_model_weights(config: FoundationModelWeightsConfig, data_dir: DataDirectory) -> Path:
    try:
        run(['git', 'lfs', 'install'], check=True)
    except:
        raise RuntimeError("git lfs is not installed so we cannot clone the model weights")
    output_dir = data_dir.subdir("foundation_model_weights")
    run(
        ['git', 'clone', '--depth', '1', f"https://huggingface.co/{config.huggingface_repo}", "."],
        cwd=output_dir,
        check=True,
    )
    return output_dir

@asset
def instruction_data(data_dir: DataDirectory) -> Path:
    output_file = data_dir.subdir("instruction_data") / "instruction_data.json"
    input_file = Path(__file__).resolve().parent.parent / "mock_data.json"

    with open(input_file, "r") as f:
        input_json = json.load(f)

    # synthetically create 50k training examples
    examples = []
    for name, state in input_json.items():
        examples.append({
            "instruction": json.dumps({"method": "get_us_state_of_residence", "name": name}),
            "input": "",
            "output": json.dumps({"status": "ok", "us_state": state})
        })

    with open(output_file, "w") as f:
        json.dump(examples, f)

    return output_file


@asset
def lora_weights(
    data_dir: DataDirectory, instruction_data: Path, foundation_model_weights: Path
) -> Path:
    output_dir = data_dir.subdir("lora_weights")
    finetune_alpaca_lora_model(
        FinetuneConfig(
            base_model=foundation_model_weights,
            output_dir=output_dir,
            data_path=instruction_data,
        )
    )
    return output_dir


@asset
def model_checkpoint(
    lora_weights: Path, data_dir: DataDirectory, foundation_model_weights: Path
) -> Path:
    output_dir = data_dir.subdir("model_checkpoint")
    export_alpaca_lora_checkpoint(
        ExportCheckpointConfig(
            base_model=foundation_model_weights,
            lora_weights=lora_weights,
            output_dir=output_dir,
        )
    )
    return output_dir

def get_llama_cpp():
    return Path(__file__).resolve().parent / ".." / "llama.cpp"

@asset
def ggml_unquantized(
    data_dir: DataDirectory,
    foundation_model_weights: Path,
    model_checkpoint: Path,
) -> Path:
    output_file = data_dir.subdir("ggml_unquantized") / "ggml-model.bin"
    run([
        sys.executable,
        "-u",
        get_llama_cpp() / "convert.py",
        "--vocab-dir",
        foundation_model_weights,
        "--outfile", output_file,
        model_checkpoint,
    ], check=True)
    return output_file

@asset
def ggml_quantized(data_dir: DataDirectory, ggml_unquantized: Path):
    output_file = data_dir.subdir("ggml_quantized") / "ggml-model-q4_0.bin"
    run([
        get_llama_cpp() / "quantize",
        ggml_unquantized,
        output_file,
        "q4_0"
    ], check=True)
    print(f"Your model is now complete! Chat with it by running: {get_llama_cpp() / 'main'} -i -m {output_file}")
    return output_file
