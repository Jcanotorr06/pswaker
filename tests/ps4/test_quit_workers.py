"""Real worker loop bodies and SDK shutdown; asset/display services are isolated."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

GAME = os.environ.get('PSWAKER_GAME_ROOT')


def worker_method(source, signature):
    """Keep the production body verbatim; do not copy its queue protocol into the test."""
    text = source.read_text()
    text = text[text.index(signature):]
    # Each #else branch is excluded by the harness defines and may repeat an opening brace.
    text = re.sub(r'^#else\n.*?^#endif\n', '#endif\n', text, flags=re.M | re.S)
    depth = 1
    end = text.index('{') + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[:end]


@unittest.skipUnless(GAME and shutil.which('clang++-21'),
                     'Prepared game and Linux compiler required')
class QuitWorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix='pswaker-quit-workers-')
        cls.addClassCleanup(cls.directory.cleanup)
        output = Path(cls.directory.name)
        game = Path(GAME) / 'src/switchwaker'
        sdk = game / 'native/sdk'
        files = [('JKernel/JKRAramStream.cpp', 'void* JKRAramStream::run() {'),
                 ('JKernel/JKRDecomp.cpp', 'void* JKRDecomp::run() {'),
                 ('JUtility/JUTException.cpp', 'void* JUTException::run() {'),
                 ('JKernel/JKRAram.cpp', 'void* JKRAram::run() {'),
                 ('JAudio/JASAudioThread.cpp',
                  'void* JASystem::TAudioThread::audioproc(void*) {')]
        methods = '\n\n'.join(worker_method(game / 'game/src/JSystem' / file, signature)
                               for file, signature in files)
        source = output / 'workers.cpp'
        source.write_text(Path(__file__).with_name('quit-workers.cpp').read_text().replace(
            '// WORKER_METHODS', methods))
        cls.binary = output / 'workers'
        sdk_sources = ['OSThread.cpp', 'OSMutex.cpp', 'OSInterrupt.cpp', 'OSAlarm.cpp',
                       'OSMessage.cpp', 'OSContext.cpp']
        result = subprocess.run([
            'clang++-21', '-std=c++23', '-D__ORBIS__', '-DTARGET_PC', '-pthread',
            '-ftrivial-auto-var-init=zero',
            '-ffunction-sections', '-fdata-sections', '-Wl,--gc-sections',
            '-I', str(sdk / 'include'), '-I', str(Path(GAME) / 'src/aurora/include'),
            *[str(sdk / 'src/os' / file) for file in sdk_sources], str(source),
            '-o', str(cls.binary)
        ], capture_output=True, text=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)

    def check_shutdown(self, scenario):
        result = subprocess.run([str(self.binary), scenario], capture_output=True,
                                text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('selected worker loops ended and joined', result.stdout)

    def test_idle_workers_return_from_blocked_receives_on_shutdown(self):
        self.check_shutdown('idle')

    def test_workers_process_valid_commands_then_stop_without_reusing_a_message(self):
        self.check_shutdown('after-work')

    def test_each_worker_independently_handles_shutdown(self):
        for worker in ['aram', 'decomp', 'exception', 'piece', 'audio']:
            with self.subTest(worker=worker):
                self.check_shutdown(worker)
