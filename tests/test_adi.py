#!/usr/bin/env pytest -vs
"""Tests for example."""

import sys
from unittest.mock import patch

import pytest

from adi import assessment_data_import as adi

# define sources of version string
PROJECT_VERSION = adi.__version__


def test_stdout_version(capsys):
    """Verify that version string sent to stdout agrees with the module version."""
    with pytest.raises(SystemExit):
        with patch.object(sys, "argv", ["bogus", "--version"]):
            adi.main()
    captured = capsys.readouterr()
    assert (
        captured.out == f"{PROJECT_VERSION}\n"
    ), "standard output by '--version' should agree with module.__version__"
