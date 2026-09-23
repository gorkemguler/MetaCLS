"""The portable launcher's worker must not resolve a user's unrelated CLI."""
import importlib.util
import subprocess
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    'desktop_runtime', Path(__file__).resolve().parents[1] / 'platform/macos/desktop_runtime.py'
)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def test_frozen_uses_itself_even_with_override(monkeypatch):
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    monkeypatch.setenv('METACLS', '/unrelated/metacls')
    assert runtime.cli_command() == [sys.executable, '--cli']


def test_unsupported_and_directory_are_not_reported_clean(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime, 'cli_command', lambda: ['metacls'])
    unsupported = tmp_path / 'notes.txt'
    unsupported.write_text('Private text')
    lines = runtime.scrub_paths([str(unsupported), str(tmp_path)])
    assert lines[-1] == '-- scrubbed 0, failed 0, skipped 2 --'


def test_worker_uses_absolute_paths_and_reports_residual(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime, 'cli_command', lambda: ['bundle', '--cli'])
    file = tmp_path / '- private file.pdf'
    file.touch()

    def run(command, **kwargs):
        assert command[-2:] == ['--', str(file)]
        assert command[:2] == ['bundle', '--cli']
        assert kwargs['timeout'] == 300
        return subprocess.CompletedProcess(command, 2, 'residual metadata', '')

    monkeypatch.setattr(runtime.subprocess, 'run', run)
    lines = runtime.scrub_paths([str(file)])
    assert 'metadata remains' in lines[0]
    assert lines[-1] == '-- scrubbed 0, failed 1, skipped 0 --'


def test_timeout_does_not_abandon_remaining_files(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime, 'cli_command', lambda: ['bundle', '--cli'])
    first, second = tmp_path / 'first.pdf', tmp_path / 'second.pdf'
    first.touch()
    second.touch()

    def run(command, **kwargs):
        if command[-1] == str(first):
            raise subprocess.TimeoutExpired(command, kwargs['timeout'])
        return subprocess.CompletedProcess(command, 0, '', '')

    monkeypatch.setattr(runtime.subprocess, 'run', run)
    lines = runtime.scrub_paths([str(first), str(second)])
    assert lines[-1] == '-- scrubbed 1, failed 1, skipped 0 --'
