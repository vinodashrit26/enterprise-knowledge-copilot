"""Errors raised by the model client."""


class LLMError(Exception):
    """Base class for every model client error."""


class LLMTemporaryError(LLMError):
    """A failure that may succeed if tried again, such as a timeout."""


class LLMPermanentError(LLMError):
    """A failure that will not succeed if repeated, such as a bad API key."""
