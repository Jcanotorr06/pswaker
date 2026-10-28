"""Shared, read-only image policy and private output checks for CLI and desktop."""
from pathlib import Path
import sys
import tempfile

from disc_image import CONTRACT, require, validate

APPLICATION_ROOT = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parents[2]


def validate_selection(image: Path, output: Path) -> dict:
    """Validate afresh; never authorize assembly from a cached desktop result."""
    destination = output.resolve()
    require(not destination.exists(), 'Output already exists; choose a new private assembly directory')
    require(not destination.is_relative_to(APPLICATION_ROOT),
            'Complete packages must be assembled outside the repository/application folder')
    report = validate(image)
    require(destination.parent.is_dir(), 'Output parent directory must already exist')
    # Probe only an app-owned temporary file, never an existing package or image.
    with tempfile.TemporaryFile(prefix='.pswaker-access-', dir=destination.parent) as probe:
        probe.write(b'PSWaker output access check')
        probe.flush()
    return report
