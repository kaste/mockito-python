#!/usr/bin/env python
from __future__ import annotations

import argparse
import asyncio
import itertools
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

import yaml

FALLBACK_PYTHONS = ("3.8", "3.9", "3.10", "3.11", "3.12", "3.13", "3.14")
CI_WORKFLOW = Path(".github/workflows/test-lint-go.yml")
RUNNER_DIR = Path(".runner")
SPINNER_FRAMES = "|/-\\"
SPINNER_INTERVAL_SECONDS = 0.1

PENDING = "pending"
RUNNING = "running"
FAILED_HINT = "failed-hint"
PASSED = "passed"
FAILED = "failed"

ANSI_RESET = "\033[0m"
ANSI_WHITE = "\033[37m"
ANSI_GREEN = "\033[32m"
ANSI_RED = "\033[31m"

PYTEST_PROGRESS_RE = re.compile(r"([.FEsxX]+)\s*(\[[^\]]+\])?\s*$")


@dataclass
class RunState:
    version: str
    status: str = PENDING
    stdout: list[str] = field(default_factory=list)
    stderr: list[str] = field(default_factory=list)
    return_code: int = -1
    outcome_file: Path | None = None


def main() -> int:
    args, pytest_args = parse_arguments()
    versions = args.versions or get_default_versions()
    max_parallel = args.max_parallel or len(versions)

    prepare_runner_dir(RUNNER_DIR, recreate_envs=args.recreate_envs)

    try:
        animate = sys.stdout.isatty()
        return asyncio.run(
            run_matrix(
                versions=versions,
                pytest_args=pytest_args,
                max_parallel=max_parallel,
                use_color=animate,
                animate=animate,
                frozen=not args.no_frozen,
            )
        )
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130


async def run_matrix(
    versions: Sequence[str],
    pytest_args: Sequence[str],
    max_parallel: int,
    use_color: bool,
    animate: bool,
    frozen: bool,
) -> int:
    states = [RunState(version=version) for version in versions]
    by_version = {state.version: state for state in states}
    semaphore = asyncio.Semaphore(max_parallel)

    stop_spinner = asyncio.Event()
    spinner_task = None
    if animate:
        spinner_task = asyncio.create_task(
            render_spinner(states, stop_spinner, use_color)
        )
    else:
        print("Running pytest for:", ", ".join(versions))

    tasks = [
        asyncio.create_task(
            run_single_version(
                state=by_version[version],
                semaphore=semaphore,
                pytest_args=pytest_args,
                frozen=frozen,
            )
        )
        for version in versions
    ]

    await asyncio.gather(*tasks)

    stop_spinner.set()
    if spinner_task is not None:
        await spinner_task

    failures = [state for state in states if state.status == FAILED]
    if not failures:
        print("All test runs passed.")
        return 0

    print("Failed versions:", ", ".join(state.version for state in failures))
    print("Failure logs:")
    for state in failures:
        print("-", state.outcome_file)

    return 1


async def run_single_version(
    state: RunState,
    semaphore: asyncio.Semaphore,
    pytest_args: Sequence[str],
    frozen: bool,
) -> None:
    async with semaphore:
        state.status = RUNNING
        command = build_command(state.version, pytest_args, frozen)

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=build_subprocess_env(state.version),
        )

        assert process.stdout is not None
        assert process.stderr is not None

        stdout_task = asyncio.create_task(
            collect_stream(
                process.stdout,
                state.stdout,
                on_line=lambda line: update_failure_hint(state, line),
            )
        )
        stderr_task = asyncio.create_task(collect_stream(process.stderr, state.stderr))

        state.return_code = await process.wait()
        await asyncio.gather(stdout_task, stderr_task)

        if state.return_code == 0:
            state.status = PASSED
            return

        state.status = FAILED
        state.outcome_file = write_outcome(
            state.version,
            command,
            state.return_code,
            state.stdout,
            state.stderr,
        )


async def render_spinner(
    states: Sequence[RunState],
    stop_event: asyncio.Event,
    use_color: bool,
) -> None:
    spinner = itertools.cycle(SPINNER_FRAMES)
    last_width = 0

    while not stop_event.is_set():
        line = render_status_line(next(spinner), states, use_color)
        last_width = rewrite_line(line, last_width)
        await asyncio.sleep(SPINNER_INTERVAL_SECONDS)

    final_symbol = "✔" if all(state.status == PASSED for state in states) else "✘"
    final_line = render_status_line(final_symbol, states, use_color)
    rewrite_line(final_line, last_width)
    sys.stdout.write("\n")
    sys.stdout.flush()


def parse_arguments() -> tuple[argparse.Namespace, Sequence[str]]:
    parser = argparse.ArgumentParser(
        description=(
            "Run pytest against all supported Python versions in parallel. "
            "Use -p 3.8 -p 3.14 to run specific versions only. "
            "Additional arguments are passed to pytest."
        )
    )
    parser.add_argument(
        "-p",
        "--python",
        dest="versions",
        action="append",
        help="Python version to run (may be used multiple times).",
    )
    parser.add_argument(
        "--max-parallel",
        type=int,
        default=0,
        help="Maximum number of concurrent runs (default: all selected versions).",
    )
    parser.add_argument(
        "--no-frozen",
        action="store_true",
        help="Do not pass --frozen to uv run.",
    )
    parser.add_argument(
        "--recreate-envs",
        action="store_true",
        help="Delete and recreate per-version environments in .runner/.",
    )
    return parser.parse_known_args()


def get_default_versions() -> list[str]:
    versions = load_versions_from_ci_workflow(CI_WORKFLOW)
    if versions:
        return versions
    return list(FALLBACK_PYTHONS)


def load_versions_from_ci_workflow(path: Path) -> list[str]:
    if not path.exists():
        return []

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        versions = data["jobs"]["test"]["strategy"]["matrix"]["python-version"]
        if not isinstance(versions, list):
            raise TypeError("python-version is not a list")
        if not all(isinstance(version, str) for version in versions):
            raise TypeError("python-version list must only contain strings")
        return versions
    except (OSError, yaml.YAMLError, KeyError, TypeError):
        print("could not read test matrix from test-lint-go.yml", file=sys.stderr)
        return []


def prepare_runner_dir(path: Path, recreate_envs: bool) -> None:
    path.mkdir(parents=True, exist_ok=True)

    for outcome in path.glob("outcome-*.txt"):
        outcome.unlink()

    if not recreate_envs:
        return

    for env_dir in path.glob(".venv-*"):
        if env_dir.is_dir():
            shutil.rmtree(env_dir)


def build_command(version: str, pytest_args: Sequence[str], frozen: bool) -> list[str]:
    command = ["uv", "run"]
    if frozen:
        command.append("--frozen")
    command.extend(["-p", version, "pytest"])
    command.extend(pytest_args)
    return command


def build_subprocess_env(version: str) -> dict[str, str]:
    environment = os.environ.copy()
    environment["UV_PROJECT_ENVIRONMENT"] = str(
        RUNNER_DIR / (".venv-{}".format(version))
    )
    return environment


def render_status_line(symbol: str, states: Sequence[RunState], use_color: bool) -> str:
    versions = [
        colorize(state.version, color_for_status(state.status), use_color)
        for state in states
    ]
    return "{}  {}".format(symbol, "  ".join(versions))


def rewrite_line(line: str, last_width: int) -> int:
    width = len(strip_ansi(line))
    padding = " " * max(last_width - width, 0)
    sys.stdout.write("\r{}{}".format(line, padding))
    sys.stdout.flush()
    return width


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def colorize(text: str, color: str, use_color: bool) -> str:
    if not use_color:
        return text
    return "{}{}{}".format(color, text, ANSI_RESET)


def color_for_status(status: str) -> str:
    if status == PASSED:
        return ANSI_GREEN
    if status in (FAILED_HINT, FAILED):
        return ANSI_RED
    return ANSI_WHITE


def update_failure_hint(state: RunState, line: str) -> None:
    # One-way transition: RUNNING -> FAILED_HINT.
    # We never reset back to RUNNING from stream output.
    if state.status != RUNNING:
        return

    if has_failure_hint(line):
        state.status = FAILED_HINT


def has_failure_hint(line: str) -> bool:
    if " FAILED " in line or line.startswith("FAILED "):
        return True

    progress_match = PYTEST_PROGRESS_RE.search(line.strip())
    if not progress_match:
        return False

    return "F" in progress_match.group(1)


async def collect_stream(
    stream: asyncio.StreamReader,
    sink: list[str],
    on_line=None,
) -> None:
    while True:
        chunk = await stream.readline()
        if not chunk:
            break

        line = chunk.decode("utf-8", errors="replace")
        sink.append(line)

        if on_line is not None:
            on_line(line)


def write_outcome(
    version: str,
    command: Sequence[str],
    return_code: int,
    stdout: Sequence[str],
    stderr: Sequence[str],
) -> Path:
    target = RUNNER_DIR / "outcome-{}.txt".format(version)
    command_line = subprocess.list2cmdline(list(command))

    content = [
        "command: {}".format(command_line),
        "exit_code: {}".format(return_code),
        "",
        "--- stdout ---",
        "",
        "".join(stdout),
        "",
        "--- stderr ---",
        "",
        "".join(stderr),
    ]
    target.write_text("\n".join(content), encoding="utf-8")
    return target


if __name__ == "__main__":
    raise SystemExit(main())
