#pragma once
#include "pswaker/menu-pictures.h"
#include "JSystem/J2DGraph/J2DPrint.h"
#include "m_Do/m_Do_ext.h"
#include "dolphin/mtx.h"
#include "dolphin/gx/GXTransform.h"

// Native 608x448 UI coordinates: a separate 544-pixel footer row preserves the
// original instruction words and icons. Even two nine-character targets fit
// comfortably at 16 pixels. No layout pictures or game text are copied here.
inline void pswaker_menu_draw_instruction(PswakerMenuInstruction instruction) {
    JUTFont* font = mDoExt_getMesgFont();
    if (font == NULL) return;
    Mtx matrix;
    MTXIdentity(matrix);
    GXLoadPosMtxImm(matrix, 0);
    GXSetCurrentMtx(0);
    J2DPrint print(font, 0.0f, 18.0f, 0x000000FF, 0x000000FF, 0x00000000, 0xFFFFFFFF);
    print.setFontSize(16.0f, 16.0f);
    print.printReturn(pswaker_menu_instruction(instruction), 544.0f, 18.0f,
        HBIND_CENTER, VBIND_TOP, 33.0f, 425.0f, 255);
    print.locate(0.0f, 0.0f);
    print.mCharColor = 0xFFFFFFFF;
    print.mGradColor = 0xFFFFFFFF;
    print.printReturn(pswaker_menu_instruction(instruction), 544.0f, 18.0f,
        HBIND_CENTER, VBIND_TOP, 32.0f, 424.0f, 255);
}
