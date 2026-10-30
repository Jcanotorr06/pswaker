"""Integration checks of the inventoried pinned camera hooks, not hardware evidence."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


GAME = os.environ.get('PSWAKER_GAME_ROOT')


@unittest.skipUnless(GAME and shutil.which('clang++-21'),
                     'Set PSWAKER_GAME_ROOT to the prepared game; Linux compiler required')
class CameraHookIntegrationTests(unittest.TestCase):
    def test_item_aiming_inventory_includes_direct_pad_and_polar_stick_readers(self):
        game = Path(GAME) / 'src/switchwaker/game/src/d'
        ship = (game / 'actor/d_a_ship.cpp').read_text().split('BOOL daShip_c::procCannon() {', 1)[1]
        ship = ship.split('/*', 1)[0]
        cannon = (game / 'actor/d_a_canon.cpp').read_text().split('void daCanon_c::PadMove() {', 1)[1]
        cannon = cannon.split('/*', 1)[0]
        for reader in [ship, cannon]:
            self.assertIn('pc_camera_invert_x()', reader)
            self.assertIn('pc_camera_invert_y()', reader)
        player = (game / 'actor/d_a_player_main.cpp').read_text()
        self.assertIn('dCam_getBody()->CalcSubjectAngle(&local_16, &local_18)', player)
        for file in ['d_a_player_bow.inc', 'd_a_player_boomerang.inc', 'd_a_player_hook.inc',
                     'd_a_player_rope.inc', 'd_a_player_ship.inc', 'd_a_player_crawl.inc']:
            self.assertIn('setBodyAngleToCamera()', (game / 'actor' / file).read_text())

    def test_prepared_camera_readers_reverse_only_selected_semantic_axes(self):
        game = Path(GAME) / 'src/switchwaker'
        source = (game / 'game/src/d/d_camera.cpp').read_text()
        cstick = re.search(r'static inline f32 dCamera_cStickX.*?(?=#undef)', source, re.S)
        self.assertIsNotNone(cstick)
        subject = source.split('bool dCamera_c::CalcSubjectAngle(', 1)[1]
        # Compile the real reader expressions, including the maintained PS4 patch.
        # Do not emulate native camera state, limits, actor transforms or rendering.
        reads = re.search(r'    fVar6 = CPad_GET_STICK_POS_X.*?(?=\n    if \(is_player)', subject, re.S)
        self.assertIsNotNone(reads)
        assert cstick is not None and reads is not None
        self.assertIn('pc_camera_invert_x()', reads[0])
        self.assertIn('pc_camera_invert_y()', reads[0])
        # The main-stick cache still represents movement/follow input, never aim inversion.
        self.assertIn('mStickMainPosXLast = CPad_GET_STICK_POS_X(mPadId);', source)
        self.assertIn('mStickMainPosYLast = CPad_GET_STICK_POS_Y(mPadId);', source)
        self.assertIn('#define CPad_GET_SUBSTICK_POS_X(padNo) dCamera_cStickX(padNo)', source)
        self.assertIn('#define CPad_GET_SUBSTICK_POS_Y(padNo) dCamera_cStickY(padNo)', source)
        ship = (game / 'game/src/d/actor/d_a_ship.cpp').read_text()
        polar = re.search(r'            float aimY =.*?(?=            m0396 \+= aimY;)', ship, re.S)
        cannon = (game / 'game/src/d/actor/d_a_canon.cpp').read_text()
        direct = re.search(r'    f32 stickX = pad->mMainStickPosX;.*?(?=    s16 target1)', cannon, re.S)
        self.assertIsNotNone(polar)
        self.assertIsNotNone(direct)
        assert polar is not None and direct is not None
        code = r'''
#include <cassert>
#include "pc/pc_controls.h"
using f32 = float;
float rawX = .4f, rawY = -.6f;
float cM_ssin(int) { return rawX; }
float cM_scos(int) { return rawY; }
struct Pad { float mMainStickPosX, mMainStickPosY; };
#define CPad_GET_STICK_POS_X(pad) rawX
#define CPad_GET_STICK_POS_Y(pad) rawY
#define CPad_GET_SUBSTICK_POS_X(pad) rawX
#define CPad_GET_SUBSTICK_POS_Y(pad) rawY
namespace pc { void writef(int, const char*, ...) {} }
'''
        code += cstick[0]
        code += '\nvoid subject(float& fVar6, float& fVar5) {\n' + reads[0] + '\n}\n'
        code += '\nvoid ship(float& x, float& y) { float adjust = 1.f / 384; int mStickMAng = 0;\n'
        code += polar[0] + '\nx = aimX; y = aimY;\n}\n'
        code += '\nvoid cannon(float& x, float& y) { Pad sample{rawX, rawY}; auto* pad = &sample;\n'
        code += direct[0] + '\nx = stickX; y = stickY;\n}\n'
        code += r'''
int main() {
    const float expectedX[] = {.4f, -.4f, .4f, -.4f};
    const float expectedY[] = {-.6f, -.6f, .6f, .6f};
    for (int combination = 0; combination < 4; ++combination) {
        pc_camera_invert_x_set(combination & 1);
        pc_camera_invert_y_set(combination & 2);
        assert(dCamera_cStickX(0) == expectedX[combination]);
        assert(dCamera_cStickY(0) == expectedY[combination]);
        float x, y;
        subject(x, y);
        assert(x == expectedX[combination] && y == expectedY[combination]);
        ship(x, y);
        assert(x == expectedX[combination] && y == expectedY[combination]);
        cannon(x, y);
        assert(x == expectedX[combination] && y == expectedY[combination]);
        assert(rawX == .4f && rawY == -.6f);
        rawX = -rawX; rawY = -rawY;
        subject(x, y);
        assert(x == -expectedX[combination] && y == -expectedY[combination]);
        ship(x, y);
        assert(x == -expectedX[combination] && y == -expectedY[combination]);
        cannon(x, y);
        assert(x == -expectedX[combination] && y == -expectedY[combination]);
        assert(dCamera_cStickX(0) == -expectedX[combination]);
        assert(dCamera_cStickY(0) == -expectedY[combination]);
        rawX = rawY = 0;
        subject(x, y);
        assert(x == 0 && y == 0);
        ship(x, y);
        assert(x == 0 && y == 0);
        cannon(x, y);
        assert(x == 0 && y == 0);
        rawX = .4f; rawY = -.6f;
    }
}
'''
        with tempfile.TemporaryDirectory(prefix='pswaker-camera-') as directory:
            root = Path(directory)
            harness = root / 'camera.cpp'
            harness.write_text(code)
            result = subprocess.run([
                'clang++-21', '-std=c++23', '-D__ORBIS__',
                '-I', str(game / 'native/include'), '-I', str(game / 'native/src/pc'),
                str(harness), str(game / 'native/src/pc/features/pc_controls.cpp'),
                '-o', str(root / 'camera')], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = subprocess.run([str(root / 'camera')], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
