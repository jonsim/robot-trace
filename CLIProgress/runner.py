import sys
import subprocess

def main():
    args = sys.argv[1:]

    cmd = [
        "robot",
        "--console=quiet",
        "--listener",
        "CLIProgress",
        *args,
    ]

    sys.exit(subprocess.call(cmd))