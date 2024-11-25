import json
import pydantic
from disko_lib.logging import ReadableMessage
from disko_lib.messages.colors import FILE, INVALID, RESET, VALUE
from ..json_types import JsonDict


def __bug_help_message(error_code: str) -> ReadableMessage:
    return ReadableMessage(
        "help",
        f"""
            Please report this bug!
            First, check if has already been reported at
                https://github.com/nix-community/disko/issues?q=is%3Aissue+{error_code}
            If not, open a new issue at
                https://github.com/nix-community/disko/issues/new?title={error_code}
            and include the full logs printed above!
        """,
    )


def bug_success_without_context(*, value: object) -> list[ReadableMessage]:
    return [
        ReadableMessage(
            "bug",
            f"""
                Success message without context!
                Returned value:
                {value}
            """,
        ),
        __bug_help_message("bug_success_without_context"),
    ]


def bug_validate_config_failed(
    *, config: JsonDict, error: pydantic.ValidationError
) -> list[ReadableMessage]:
    errors_printed = json.dumps(error.errors(), indent=2)  # type: ignore[misc]
    return [
        ReadableMessage(
            "info",
            f"""
                Evaluated configuration:
                {json.dumps(config, indent=2)}
            """,
        ),
        ReadableMessage(
            "error",
            f"""
                Validation errors:
                {errors_printed}
            """,
        ),
        ReadableMessage(
            "bug",
            f"""
                Configuration validation failed!
                Most likely, the types in python are out-of-sync with those in nix.
                The {INVALID}validation errors{RESET} and the {VALUE}evaluated configuration{RESET} are printed above.
            """,
        ),
        __bug_help_message("bug_validate_config_failed"),
    ]


def bug_unsupported_device_content_type(
    *, name: str, device: str, type: str
) -> list[ReadableMessage]:
    return [
        ReadableMessage(
            "bug",
            f"""
                Configuration for device {FILE}{device}{RESET} (name={VALUE}{name}{RESET}) specifies unsupported
                device content type {INVALID}{type}{RESET}, which was not implemented yet!
            """,
        ),
        __bug_help_message("err_unsupported_device_content_type"),
    ]


def bug_unsupported_partition_content_type(
    *, name: str, device: str, type: str
) -> list[ReadableMessage]:
    return [
        ReadableMessage(
            "bug",
            f"""
                Configuration for partition {FILE}{device}{RESET} (name={VALUE}{name}{RESET}) specifies unsupported
                partition content type {INVALID}{type}{RESET}, which was not implemented yet!
            """,
        ),
        __bug_help_message("bug_unsupported_partition_content_type"),
    ]
