"""Enums for AI Strategy Assistant data models."""

from enum import Enum


class MarketValidationLevel(str, Enum):
    """Enum for market validation levels."""
    ASSUMPTION = "assumption"
    HYPOTHESIS = "hypothesis"
    VALIDATED = "validated"
    PROVEN = "proven"


class MVPPriority(str, Enum):
    """Enum for MVP feature priorities."""
    CORE = "core"
    IMPORTANT = "important"
    FUTURE = "future"