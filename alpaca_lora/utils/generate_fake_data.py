from faker import Faker
import json
from pathlib import Path

if __name__ == "__main__":
    f = Faker()
    f.seed_instance(1234)
    examples = {}
    while len(examples) < 50000:
        examples[f.name()] = f.state()

    with open(Path(__file__).resolve().parent.parent.parent / "mock_data.json", "w") as f:
        json.dump(examples, f)