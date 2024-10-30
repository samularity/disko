#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
from typing import Any, Literal, assert_never

from disko_lib.ansi import disko_dev_ansi
from disko_lib.eval_config import eval_disko_file, eval_flake
from disko_lib.logging import LOGGER, debug, info
from disko_lib.result import DiskoError, DiskoSuccess, DiskoResult, exit_on_error
from disko_lib.types.disk import generate_config
from disko_lib.types.device import disko_dev_lsblk

Mode = Literal[
    "destroy",
    "format",
    "mount",
    "destroy,format,mount",
    "format,mount",
    "generate",
    "dev",
]


# Modes to apply an existing configuration
APPLY_MODES: list[Mode] = [
    "destroy",
    "format",
    "mount",
    "destroy,format,mount",
    "format,mount",
]
ALL_MODES: list[Mode] = APPLY_MODES + ["generate", "dev"]

MODE_DESCRIPTION: dict[Mode, str] = {
    "destroy": "Destroy the partition tables on the specified disks",
    "format": "Change formatting and filesystems on the specified disks",
    "mount": "Mount the specified disks",
    "destroy,format,mount": "Run destroy, format and mount in sequence",
    "format,mount": "Run format and mount in sequence",
    "generate": "Generate a disko configuration file from the system's current state",
    "dev": "Print information useful for developers",
}


def run_apply(
    *, mode: str, disko_file: str | None, flake: str | None, **_kwargs: dict[str, Any]
) -> DiskoResult[dict[str, Any]]:
    # match would be nicer, but mypy doesn't understand type narrowing in tuples
    if not disko_file and not flake:
        return DiskoError.single_message("ERR_MISSING_ARGUMENTS", {}, "validate args")
    if not disko_file and flake:
        return eval_flake(flake)
    if disko_file and not flake:
        return eval_disko_file(Path(disko_file))

    return DiskoError.single_message("ERR_TOO_MANY_ARGUMENTS", {}, "validate args")


def run_generate() -> DiskoResult[dict[str, Any]]:
    return generate_config()


def run_dev(args: argparse.Namespace) -> DiskoResult[None]:
    match args.dev_command:
        case "lsblk":
            return disko_dev_lsblk()
        case "ansi":
            return DiskoSuccess(None, disko_dev_ansi())
        case _:
            assert_never(args.dev_command)


def run(
    args: argparse.Namespace,
) -> DiskoResult[None | dict[str, Any]]:
    if args.verbose:
        LOGGER.setLevel("DEBUG")
        debug("Enabled debug logging.")

    match args.mode:
        case None:
            return DiskoError.single_message(
                "ERR_MISSING_MODE", {"valid_modes": ALL_MODES}, "select mode"
            )
        case "generate":
            return run_generate()
        case "dev":
            return run_dev(args)
        case _:
            return run_apply(**vars(args))


def parse_args() -> argparse.Namespace:
    root_parser = argparse.ArgumentParser(
        prog="disko2",
        description="Automated disk partitioning and formatting tool for NixOS",
    )

    root_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Print more detailed output, helpful for debugging",
    )

    mode_parsers = root_parser.add_subparsers(dest="mode")

    def create_apply_parser(mode: Mode) -> argparse.ArgumentParser:
        parser = mode_parsers.add_parser(
            mode,
            help=MODE_DESCRIPTION[mode],
        )
        parser.add_argument(
            "disko_file",
            nargs="?",
            default=None,
            help="Path to the disko configuration file",
        )
        parser.add_argument(
            "--flake",
            "-f",
            help="Flake to fetch the disko configuration from",
        )
        return parser

    # Commands to apply an existing configuration
    apply_parsers = [create_apply_parser(mode) for mode in APPLY_MODES]

    # Other commands
    generate_parser = mode_parsers.add_parser(
        "generate",
        help=MODE_DESCRIPTION["generate"],
    )

    # Commands for developers
    dev_parsers = mode_parsers.add_parser(
        "dev",
        help=MODE_DESCRIPTION["dev"],
    ).add_subparsers(dest="dev_command")
    dev_parsers.add_parser("lsblk", help="List block devices the way disko sees them")
    dev_parsers.add_parser("ansi", help="Print defined ansi color codes")
    return root_parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run(args)
    output = exit_on_error(result)
    if output:
        info("Output:\n" + json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
