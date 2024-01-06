import sys
import yaml
import os

from pyspec2openapi import parse_specs


def main():
    # Check if the config file path is provided
    if len(sys.argv) < 3:
        print("Usage: pyspec2openapi <config_path> <out_path>")
        sys.exit(1)

    config_path = sys.argv[1]
    out_path = sys.argv[2]

    try:
        with open(config_path, 'r') as file:
            # Parse the YAML file
            config = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"File not found: {config_path}")
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML file: {exc}")

    config_dir = os.path.dirname(os.path.abspath(config_path))

    out = parse_specs(config, config_dir)
    with open(out_path, 'w') as file:
        file.write(yaml.dump(out, sort_keys=False))


if __name__ == "__main__":
    main()
