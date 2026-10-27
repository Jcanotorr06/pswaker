"""Data-free program payload contract shared by packaging and desktop bundling."""
import json
from pathlib import Path
import re

from disc_image import require

PROGRAM_FILES = {'eboot.bin', 'build-info.json', 'sce_sys/icon0.png', 'sce_sys/param.sfo',
                 'sce_sys/about/right.sprx', 'sce_module/libSceFios2.prx', 'sce_module/libc.prx'}


def bundled_program(bundle: Path) -> tuple[str, str]:
    """Read the identity of the fixed, maintainer-bundled game release."""
    release = json.loads((bundle / 'program/program-release.json').read_text())
    info = json.loads((bundle / 'program/stage/build-info.json').read_text())
    require(release['schema'] == 1 and release['kind'] == 'game'
            and 'diagnostic_build_id' not in info
            and isinstance(release['build_id'], str) and bool(release['build_id'])
            and info['program_build_id'] == release['build_id'],
            'The bundled release must be a matching game program')
    version = info['app_version']
    require(isinstance(version, str) and re.fullmatch(r'[0-9]{2}\.[0-9]{2}', version),
            'The bundled game version must be NN.NN')
    return version, release['build_id']
