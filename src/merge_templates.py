import glob
import os
from typing import Any

import yaml


class MergeTemplates:
    def __init__(self, api_key: str, base_url: str, provider: str):
        self.__api_key = api_key
        self.__base_url = base_url
        self.__provider = provider

    def __load_yaml(self, file_path: str) -> dict[str, Any]:
        try:
            with open(file_path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
            raise

    def merge_yaml_files(self, generated_folder: str, template_file: str, output_file: str) -> None:
        # Load and validate main template
        template_data = self.__load_yaml(template_file)

        if "include" not in template_data:
            raise ValueError("Main template must contain 'include' keyword")

        # Initialize output data
        output_data = {k: v for k, v in template_data.items() if k != "include"}

        # Process includes
        for pattern in template_data["include"]:
            folder_pattern = f"{generated_folder}/{pattern}"
            try:
                files = glob.glob(folder_pattern)
                if not files:
                    print(f"No files found for pattern: {folder_pattern}")
                    continue

                latest_file = max(files, key=os.path.getmtime)  # More efficient than sorting

                included_data = self.__load_yaml(latest_file)
                if "model_list" in output_data:
                    output_data["model_list"] = output_data.get("model_list", []) + included_data.copy()
                    print(f"Merged: {latest_file}")

            except Exception as e:
                print(f"Error processing {pattern}: {str(e)}")

        if not output_data.get("model_list"):
            raise ValueError("No model_list found in any output_data")

        # Write output
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as f:
            yaml.dump(output_data, f, sort_keys=False, default_flow_style=False)
