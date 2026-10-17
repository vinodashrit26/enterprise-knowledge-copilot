"""Tests for the package entry point."""

import pytest

from enterprise_knowledge_copilot import main


def test_main_prints_greeting(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify that main prints the greeting."""

    # Call: the function main
    main()

    # Capture: get what was printed
    captured = capsys.readouterr()

    # Assert: Verify the output
    assert captured.out == "Hello from enterprise-knowledge-copilot!\n"
