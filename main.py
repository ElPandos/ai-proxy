import logging

from src.app import App

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()],
)


# def parse_arguments() -> argparse.Namespace:
#     parser = argparse.ArgumentParser(description="Generate liteLLM templates from model provider API.")
#     parser.add_argument(
#         "--api-base-url",
#         dest="api_base_url",
#         type=str,
#         required=True,
#         help="API base URL to model provider.",
#     )
#     parser.add_argument(
#         "--api-key",
#         dest="api_key",
#         type=str,
#         required=True,
#         help="API key from the provider.",
#     )
#     parser.add_argument(
#         "--provider",
#         dest="provider",
#         type=str,
#         required=True,
#         help="Provider name for liteLLM (e.g., openrouter).",
#     )
#     parser.add_argument(
#         "--filter-suffixes",
#         dest="filter_suffixes",
#         nargs="*",
#         default=[],
#         help="Suffixes to filter out model IDs (e.g., ':free'). Empty = no filtering.",
#     )
#     parser.add_argument(
#         "--main-template-file",
#         dest="main_template_file",
#         type=str,
#         required=True,
#         help="Main template file containing known LLM provider model templates.",
#     )
#     parser.add_argument(
#         "--output-file",
#         dest="output_file",
#         type=str,
#         required=True,
#         help="Output filename for the merged configuration.",
#     )
#     return parser.parse_args()


if __name__ in {"__main__", "__mp_main__"}:
    try:
        app = App()
    except Exception as e:
        logging.error(f"Error: {e}")
