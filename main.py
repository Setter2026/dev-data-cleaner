import logging

# 1. Import your modular classes from their respective files
from components.file_loader import FileLoader
from components.sanitizer import Sanitizer
from components.parser import Parser
from components.validator import Validator
from components.file_exporter import JSONExporter
from tracker import PipelineTracker
from orchestrator import PipelineOrchestrator


def test_pipeline():

    # 1. Create or get your central logger
    logger = logging.getLogger("Pipeline")
    logger.setLevel(logging.WARNING)  # Capture WARNING, ERROR, and CRITICAL

    # 2. Prevent duplicate log entries
    logger.handlers.clear()
    logger.propagate = False

    # 3. Create a uniform formatting layout for your logs
    log_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] (%(name)s) -> %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 4. Console Handler (Prints to screen)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    # 5. File Handler (Appends to a permanent text file)
    file_handler = logging.FileHandler("pipeline_errors.log", mode="a", encoding="utf-8")
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
    )

    # 3. Instantiate concrete components with loggers
    loader = FileLoader()
    sanitizer = Sanitizer()
    parser = Parser()
    validator = Validator()
    exporter = JSONExporter()
    tracker = PipelineTracker()

    # 4. Pass components into the Orchestrator
    pipeline = PipelineOrchestrator(
        file_loader=loader,
        sanitizer=sanitizer,
        parser=parser,
        validator=validator,
        exporter=exporter,
        tracker=tracker
    )

    # 5. Run pipeline on your input data
    input_file = "data/sample.txt"       # Ensure this test file exists
    output_file = "data/test_output.json"

    pipeline.run(
        input_filepath=input_file,
        output_filepath=output_file
    )

test_pipeline()