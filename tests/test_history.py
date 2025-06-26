import os
import json
import tempfile
import importlib
import sys
import pytest

def test_save_and_get_history(tmp_path, monkeypatch):
    # Patch HIST_PATH to a temp file
    temp_history = tmp_path / 'history.json'
    monkeypatch.setattr('history.HIST_PATH', str(temp_history))
    import history
    importlib.reload(history)
    # Save an interaction
    data = {'msg': 'test'}
    history.save_interaction(data)
    # Get history
    hist = history.get_history()
    assert isinstance(hist, list)
    assert hist[-1]['msg'] == 'test' 