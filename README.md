# Keyguard

A test application for biometric keystroke authentication.
It collects dwell-time statistics for a fixed phrase typed by the user and uses
those measurements to build a typing profile. The same profile can later be
used to authenticate the user by comparing new samples with the saved data

## Installation

This project uses [Poetry](https://python-poetry.org/) for dependency
management. Python 3.11 or newer is required.

```bash
poetry install --no-root
```

## Usage

Run the application with:

```bash
python -m keyguard
```

First complete a training session to create a profile. Afterwards you can use
the authentication view to verify the typing pattern.

## Building with PyInstaller

Keyguard ships with a PyInstaller specification file that collects the
application resources.  To create a standalone executable run:

```bash
poetry run pyinstaller --onefile keyguard.spec
```

The resulting binary will be available in the `dist/` directory.  You can edit
`keyguard.spec` if additional data files or options are required.


## Disclaimer
The images used in this project were taken from the
[anytype.io](https://anytype.io/) website for educational purposes only. I do
not claim ownership of these images, nor are they provided or licensed by me.
All rights, credits, and permissions for the original images remain with their
respective owners at Anytype.