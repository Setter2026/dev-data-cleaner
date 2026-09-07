class PipelineException(Exception):
    """Base exception for pipeline errors."""

class FileReadError(PipelineException): pass
class SanitizeError(PipelineException): pass
class ParseError(PipelineException): pass
