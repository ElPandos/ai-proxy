import logging
import os
import sys
from pathlib import Path
from subprocess import Popen

from dotenv import load_dotenv

from src.gather_templates import GatherTemplates
from src.merge_templates import MergeTemplates
from src.process_manager import ProcessManager


class App:
    def __init__(self) -> None:
        load_dotenv()

        self.__generated_folder_path = os.getenv("LITELLM_OUTPUT_FOLDER_PATH")
        self.__verify_folder_exists(self.__generated_folder_path)

        self.__litellm_output_folder_path = os.getenv("LITELLM_OUTPUT_FOLDER_PATH")
        self.__verify_folder_exists(self.__litellm_output_folder_path)

        self.__litellm_output_file = os.getenv("LITELLM_OUTPUT_FILE")

        self.__litellm_template_folder_path = os.getenv("LITELLM_TEMPLATE_FOLDER_PATH")
        self.__verify_folder_exists(self.__litellm_template_folder_path)

        self.__litellm_main_template_file = os.getenv("LITELLM_TEMPLATE_FILE")
        self.__verify_file_exists(self.__litellm_main_template_file)

    def __verify_folder_exists(self, folder: str) -> None:
        path = Path(folder).resolve()
        try:
            if not path.is_dir():
                os.makedirs(path, exist_ok=True)
                logging.info(f"Created folder: {path}")
            # Check for read/write/execute permissions (user, group, others)
            if not os.access(str(path), os.R_OK | os.W_OK | os.X_OK):
                raise PermissionError(f"Insufficient permissions for directory: {path}")

        except OSError as e:
            logging.error(f"Failed to create folder: {folder}: {str(e)}")
            raise

    def __verify_file_exists(self, file: str) -> None:
        path = Path(file).resolve()
        try:
            if path.is_file():
                logging.info(f"File exists: {file}")
                # Check for read/write/execute permissions (user, group, others)
                if not os.access(str(path), os.R_OK | os.W_OK | os.X_OK):
                    raise PermissionError(f"Insufficient permissions for file: {file}")
        except OSError as e:
            raise FileExistsError("File does not exists: {str(e)}")

    def __gatherer(self, api_key: str, base_url: str, provider: str, filter: str) -> None:
        try:
            logging.info(f"Fetching models from: {base_url}")

            # Initialize class instance
            handler = GatherTemplates(base_url, api_key, provider)

            models = handler.fetch_models()
            filtered_model_ids = handler.filter_models(models, filter)

            if not filtered_model_ids:
                logging.warning("No matching models found.")
                sys.exit(1)

            templates = handler.generate_templates(filtered_model_ids)

            logging.info(f"Saving templates...")
            handler.verify_generated_folder_exists(self.__generated_folder)

            # handler.save_templates_to_json(templates, generated_folder, args.provider)
            handler.save_templates_to_yaml(templates, self.__generated_folder, provider)
            logging.info("Done")
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            sys.exit(1)

    def __merger(self) -> None:
        try:
            logging.info(f"Merging templates based on: {self.__litellm_main_template_file}")
            handler = MergeTemplates()
            handler.merge_yaml_files(
                self.__generated_folder_path,
                Path(self.__litellm_template_folder_path + "/" + self.__litellm_main_template_file),
                Path(self.__litellm_output_folder_path + "/" + self.__litellm_output_file),
            )
            print(f"Created configuration file: {self.__litellm_output_file}\n")
        except Exception as e:
            logging.error(f"Error: {str(e)}")

    def run(self) -> None:
        self.__process_manager = ProcessManager()
        self.__process_manager.run(self.__litellm_output_folder_path, self.__litellm_output_file)

    def update(self) -> None:
        self.__gatherer(
            os.getenv("ENV_DUMMY_API_KEY"),
            os.getenv("LMSTUDIO_API_BASE_URL"),
            os.getenv("LMSTUDIO_LITELLM_PROVIDER"),
            os.getenv("LMSTUDIO_FILTER"),
        )
        self.__GatherTemplates(
            os.getenv("ENV_DUMMY_API_KEY"),
            os.getenv("ERICAI_API_BASE_URL"),
            os.getenv("ERICAI_LITELLM_PROVIDER"),
            os.getenv("ERICAI_FILTER"),
        )
        self.__GatherTemplates(
            os.getenv("ENV_OPENROUTER_API_KEY"),
            os.getenv("OPENROUTER_API_BASE_URL"),
            os.getenv("OPENROUTER_LITELLM_PROVIDER"),
            os.getenv("OPENROUTER_FILTER"),
        )

        self.__merger()

    def terminate_all(self) -> None:
        self.__process_manager.terminate_all()
