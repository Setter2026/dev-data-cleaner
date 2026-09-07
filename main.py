import argparse
import logging
from pathlib import Path

from components.file_exporter import JSONExporter
from components.file_loader import FileLoader
from components.parser import Parser
from components.sanitizer import Sanitizer
from components.validator import Validator
from orchestrator import PipelineOrchestrator
from tracker import PipelineTracker


def setup_logging(verbose: bool) -> None:
    """Configures console log verbosity."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
        logging.FileHandler("data/pipeline.log"), # Writes to file
        logging.StreamHandler()
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    """Constructs the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="dataclean",
        description="Modular, fault-tolerant text data cleaning pipeline."
    )


    parser.add_argument(
        "--input",
        type=str,
        help="Path to the raw input text file."
    )


    parser.add_argument(
        "-o", "--output",
        type=str,
        default="./data/test_output.json",
        help="Path where cleaned JSON records should be saved. (Default: ./output/clean_data.json)"
    )

    parser.add_argument(
        "-e", "--errors",
        type=str,
        default="./data/errors.json",
        help="Path where quarantined error records should be saved. (Default: ./output/errors.json)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable DEBUG level logging to inspect line-by-line processing."
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # 1. Setup Logging based on -v flag
    setup_logging(args.verbose)
    logger = logging.getLogger("CLI")

    # 2. Ensure Output Directories Exist
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.errors).parent.mkdir(parents=True, exist_ok=True)

    # 3. Instantiate Pipeline Dependencies
    loader = FileLoader()
    sanitizer = Sanitizer()
    parser_comp = Parser()
    validator = Validator()
    exporter = JSONExporter()
    tracker = PipelineTracker()

    orchestrator = PipelineOrchestrator(
        file_loader=loader,
        sanitizer=sanitizer,
        parser=parser_comp,
        validator=validator,
        exporter=exporter,
        tracker=tracker
    )

    # 4. Execute Pipeline
    try:
        orchestrator.run(
            input_filepath=args.input,
            output_filepath=args.output
        )
    except FileNotFoundError:
        logger.critical(f"Specified input file not found: '{args.input}'")




if __name__ == "__main__":
    main()