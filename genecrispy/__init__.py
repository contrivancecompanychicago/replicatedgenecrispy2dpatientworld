"""GENE CRISpy Python package, version 0.2.0."""

from .agent import GeneCrispyAgent, MAX_INPUT_BYTES

__version__ = "0.2.0"

__all__ = ["GeneCrispyAgent", "MAX_INPUT_BYTES", "__version__"]

from .education import get_m1_genetics_curriculum, get_genetics_lesson
