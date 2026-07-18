from enum import IntEnum


class ApplicationExitCode(IntEnum):
    """
    Standard exit codes for DMI executable entry points.
    """

    SUCCESS = 0

    CONFIGURATION_ERROR = 10

    RUNTIME_ERROR = 20

    CLIENT_FAILURE = 30

    ALREADY_RUNNING = 40


EXIT_SUCCESS = int(
    ApplicationExitCode.SUCCESS
)

EXIT_CONFIGURATION_ERROR = int(
    ApplicationExitCode.CONFIGURATION_ERROR
)

EXIT_RUNTIME_ERROR = int(
    ApplicationExitCode.RUNTIME_ERROR
)

EXIT_CLIENT_FAILURE = int(
    ApplicationExitCode.CLIENT_FAILURE
)

EXIT_ALREADY_RUNNING = int(
    ApplicationExitCode.ALREADY_RUNNING
)