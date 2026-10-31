"""Verified private assembly assets, separate from the data-free program release."""
from contextlib import closing
import json
import re
import sqlite3

from build_operation import copy_file
from disc_image import require
from package_artifact import PIPELINE_SEED, digest, inventory, validate_pipeline_seed

ASSET_DIRECTORY = 'assembly-assets'
SEED_MANIFEST = 'pipeline-seed.json'


def checked_pipeline_asset(directory):
    remedy = 'Required shader seed: prepare a compatible pipeline-seed asset or reinstall the complete application.'
    require(directory.is_dir(), remedy)
    files = inventory(directory)
    require(set(files) == {PIPELINE_SEED, SEED_MANIFEST}, remedy)
    try:
        report = json.loads((directory / SEED_MANIFEST).read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise ValueError(f'Required shader seed metadata cannot be read: {error}. {remedy}') from error
    require(isinstance(report, dict) and report.get('schema') == 1
            and report.get('installed_path') == '/app0/' + PIPELINE_SEED
            and report.get('sha256') == files[PIPELINE_SEED],
            'Required shader seed differs from pipeline-seed.json. ' + remedy)
    sources = report.get('source_files')
    require(isinstance(sources, dict) and bool(sources) and all(
        isinstance(source, dict) and isinstance(source.get('bytes'), int) and source['bytes'] >= 0
        and isinstance(source.get('sha256'), str) and re.fullmatch('[0-9a-f]{64}', source['sha256'])
        for source in sources.values()), 'Required shader seed has invalid source provenance. ' + remedy)
    path = directory / PIPELINE_SEED
    # Prepared assets are standalone snapshots. Never create/checkpoint source sidecars.
    try:
        with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro&immutable=1', uri=True)) as db:
            details = validate_pipeline_seed(db)
    except (ValueError, sqlite3.Error) as error:
        raise ValueError(f'Required shader seed is invalid or renderer-incompatible: {error}. {remedy}') from error
    require(all(report.get(key) == value for key, value in details.items()),
            'Required shader seed records differ from pipeline-seed.json. ' + remedy)
    size = path.stat().st_size
    require(report.get('bytes', size) == size, 'Required shader seed size differs from pipeline-seed.json')
    require(inventory(directory) == files, 'Required shader seed changed during validation; retry with stable assets')
    return {**report, 'bytes': size, 'asset_manifest_sha256': files[SEED_MANIFEST]}


def install_pipeline_asset(directory, stage):
    report = checked_pipeline_asset(directory)
    target = stage / PIPELINE_SEED
    copy_file(directory / PIPELINE_SEED, target)
    require(digest(target) == report['sha256'] and target.stat().st_size == report['bytes'],
            'Required shader seed changed while copying; retry with stable assets')
    return report
