import json
import logging
import os
from datetime import datetime
from typing import Dict, List

import requests
import yaml


class GatherTemplates:
    def __init__(self, api_base_url: str, api_key: str, provider: str):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.provider = provider

    def fetch_models(self) -> List[Dict[str, object]]:
        try:
            logging.info(f"Fetching models from {self.api_base_url}/models")
            response = requests.get(f"{self.api_base_url}/models", timeout=10)
            response.raise_for_status()

            data = response.json()
            if "data" not in data or not isinstance(data["data"], list):
                raise RuntimeError("Invalid API response: 'data' field missing or incorrect.")

            return data["data"]

        except requests.RequestException as e:
            logging.error(f"Failed to fetch models: {str(e)}")
            raise RuntimeError(f"Failed to fetch models: {e}")

        except json.JSONDecodeError:
            logging.error("Failed to parse API response as JSON.")
            raise RuntimeError("Failed to parse API response as JSON.")

    def filter_models(self, models: List[Dict], allowed_suffixes: List[str]) -> List[str]:
        if not allowed_suffixes:
            return [str(model["id"]) for model in models if "id" in model]

        filtered = []
        for model in models:
            model_id = model.get("id", "")
            if any(model_id.endswith(suffix) for suffix in allowed_suffixes):
                filtered.append(model_id)

        return filtered

    @staticmethod
    def _convert_provider(provider: str) -> str:
        if provider.lower() == "openai":
            return "ericai"
        return provider

    def generate_template(self, model_id: str) -> Dict:
        return {
            "model_name": f"litellm - {self._convert_provider(self.provider)} - [{self.provider.lower()}/{model_id}]",
            "litellm_params": {
                "model": f"{self.provider}/{model_id}",
                "api_base": self.api_base_url,
                "api_key": self.api_key,
                "temperature": 0.8,
            },
        }

    def generate_templates(self, model_ids: List[str]) -> List[Dict]:
        return [self.generate_template(mid) for mid in model_ids]

    def verify_generated_folder_exists(self, folder_path: str) -> None:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logging.info(f"Created folder: {folder_path}")

    def get_timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d-%H%M%S")

    def save_templates_to_json(self, templates: List[Dict], folder_path: str, filename: str) -> None:
        filename_modified = filename.replace("_", "")
        if filename_modified.lower() == "openai":
            filename_modified = "ericai"

        file_path = os.path.join(folder_path, f"{self.get_timestamp()}_{self._convert_provider(self.provider)}.json")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(templates, f, indent=4)

        logging.info(f"(JSON) Templates saved to: {file_path}")

    def save_templates_to_yaml(self, templates: List[Dict], folder_path: str, filename: str) -> None:
        filename_modified = filename.replace("_", "")
        if filename_modified.lower() == "openai":
            filename_modified = "ericai"

        file_path = os.path.join(folder_path, f"{self.get_timestamp()}_{filename_modified}.yaml")

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(templates, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        logging.info(f"(YAML) Templates saved to: {file_path}")
