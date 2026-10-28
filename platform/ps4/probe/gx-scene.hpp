// Shared throwaway GX scene. Requires configure_gx_diagnostic() before drawing.
enum class RendererScene { Standard, AlphaR8GT, AlphaR8EQ, AlphaGR16GT, AlphaGR16EQ,
                           AlphaBGR24GT, AlphaBGR24EQ, AlphaR8GTFalse, AlphaR8EQFalse,
                           AlphaGR16GTFalse, AlphaGR16EQFalse, AlphaBGR24GTFalse, AlphaBGR24EQFalse,
                           LitSrtg, QuadTriangle, Black, ZeroBrightnessLight };
void triangle(bool white=false,unsigned width=1280,unsigned height=720,
              RendererScene scene=RendererScene::Standard,GXTexObj* source_texture=nullptr) {
  GXSetCopyClear(GXColor{8,12,28,255},GX_MAX_Z24); GXClearVtxDesc();
  GXSetVtxDesc(GX_VA_POS,GX_DIRECT); GXSetVtxDesc(GX_VA_CLR0,GX_DIRECT);
  GXSetVtxAttrFmt(GX_VTXFMT0,GX_VA_POS,GX_POS_XYZ,GX_F32,0);
  GXSetVtxAttrFmt(GX_VTXFMT0,GX_VA_CLR0,GX_CLR_RGBA,GX_RGBA8,0);
  GXSetNumChans(1); GXSetNumTexGens(white ? 1 : 0); GXSetNumTevStages(1);
  GXSetChanCtrl(GX_COLOR0A0,GX_DISABLE,GX_SRC_REG,GX_SRC_VTX,GX_LIGHT_NULL,GX_DF_NONE,GX_AF_NONE);
  if (white) {
    alignas(32) static const auto pixels=[] { std::array<u8,64> value{}; value.fill(255); return value; }();
    static GXTexObj texture{};
    static bool initialized=false;
    if (!initialized) {
      GXInitTexObj(&texture,pixels.data(),4,4,GX_TF_RGBA8,GX_CLAMP,GX_CLAMP,GX_FALSE);
      GXInitTexObjLOD(&texture,GX_NEAR,GX_NEAR,0,0,0,GX_FALSE,GX_FALSE,GX_ANISO_1);
      initialized=true;
    }
    GXSetVtxDesc(GX_VA_TEX0,GX_DIRECT);
    GXSetVtxAttrFmt(GX_VTXFMT0,GX_VA_TEX0,GX_TEX_ST,GX_F32,0);
    GXSetTexCoordGen(GX_TEXCOORD0,GX_TG_MTX2x4,GX_TG_TEX0,GX_IDENTITY);
    GXLoadTexObj(source_texture ? source_texture : &texture,GX_TEXMAP0);
    GXSetTevOrder(GX_TEVSTAGE0,GX_TEXCOORD0,GX_TEXMAP0,GX_COLOR0A0);
    GXSetTevOp(GX_TEVSTAGE0,GX_MODULATE);
  } else {
    GXSetTevOrder(GX_TEVSTAGE0,GX_TEXCOORD_NULL,GX_TEXMAP_NULL,GX_COLOR0A0);
    GXSetTevOp(GX_TEVSTAGE0,GX_PASSCLR);
  }
  GXSetCullMode(GX_CULL_NONE); GXSetZMode(GX_DISABLE,GX_ALWAYS,GX_DISABLE);
  GXSetBlendMode(GX_BM_NONE,GX_BL_ONE,GX_BL_ZERO,GX_LO_CLEAR);
  GXSetColorUpdate(GX_TRUE); GXSetAlphaUpdate(GX_TRUE);
  GXSetAlphaCompare(GX_ALWAYS,0,GX_AOP_AND,GX_ALWAYS,0);
  Mtx model{{1,0,0,0},{0,1,0,0},{0,0,1,0}};
  // C_MTXOrtho's near=0, far=1 contract maps view z=-0.5 to GX clip z=-0.5.
  Mtx44 projection{{1,0,0,0},{0,1,0,0},{0,0,-1,-1},{0,0,0,1}};
  GXLoadPosMtxImm(model,GX_PNMTX0); GXSetCurrentMtx(GX_PNMTX0); GXSetProjection(projection,GX_ORTHOGRAPHIC);
  GXSetViewport(0,0,width,height,0,1); GXSetScissor(0,0,width,height);
  if (scene>=RendererScene::AlphaR8GT && scene<=RendererScene::AlphaBGR24EQFalse) {
    constexpr GXTevOp ops[]={GX_TEV_COMP_R8_GT,GX_TEV_COMP_R8_EQ,GX_TEV_COMP_GR16_GT,
      GX_TEV_COMP_GR16_EQ,GX_TEV_COMP_BGR24_GT,GX_TEV_COMP_BGR24_EQ};
    const unsigned variant=unsigned(scene)-unsigned(RendererScene::AlphaR8GT);
    const unsigned index=variant%6;
    GXSetTevColor(GX_TEVREG0,GXColor{200,200,200,255});
    const u8 b=variant>=6 ? (index%2 ? 100 : 250) : (index%2 ? 200 : 100);
    GXSetTevColor(GX_TEVREG1,GXColor{b,b,b,255});
    GXSetTevColorIn(GX_TEVSTAGE0,GX_CC_C0,GX_CC_C1,GX_CC_ZERO,GX_CC_ZERO);
    // Write zero to C0 before the alpha half: its comparison must use latched inputs.
    GXSetTevColorOp(GX_TEVSTAGE0,GX_TEV_SUB,GX_TB_ZERO,GX_CS_SCALE_1,GX_TRUE,GX_TEVREG0);
    GXSetTevKAlphaSel(GX_TEVSTAGE0,GX_TEV_KASEL_1);
    GXSetTevAlphaIn(GX_TEVSTAGE0,GX_CA_ZERO,GX_CA_ZERO,GX_CA_KONST,GX_CA_ZERO);
    GXSetTevAlphaOp(GX_TEVSTAGE0,ops[index],GX_TB_ZERO,GX_CS_SCALE_1,GX_TRUE,GX_TEVPREV);
  } else if (scene==RendererScene::LitSrtg) {
    alignas(32) static const auto ramp=[] {
      std::array<u8,64> value{}; value.fill(255);
      // Tiled RGBA8: texel (0,0) is opaque black, all others opaque white.
      value[1]=value[32]=value[33]=0; return value;
    }();
    GXTexObj texture{};
    GXInitTexObj(&texture,ramp.data(),4,4,GX_TF_RGBA8,GX_CLAMP,GX_CLAMP,GX_FALSE);
    GXInitTexObjLOD(&texture,GX_NEAR,GX_NEAR,0,0,0,GX_FALSE,GX_FALSE,GX_ANISO_1);
    GXLoadTexObj(&texture,GX_TEXMAP0);
    GXSetChanMatColor(GX_COLOR0A0,GXColor{255,255,255,255});
    GXSetChanAmbColor(GX_COLOR0A0,GXColor{255,255,255,255});
    GXSetChanCtrl(GX_COLOR0A0,GX_ENABLE,GX_SRC_REG,GX_SRC_REG,GX_LIGHT_NULL,GX_DF_NONE,GX_AF_NONE);
    GXSetTexCoordGen(GX_TEXCOORD0,GX_TG_SRTG,GX_TG_COLOR0,GX_IDENTITY);
    GXSetTevOp(GX_TEVSTAGE0,GX_REPLACE);
  } else if (scene==RendererScene::Black) {
    GXSetTevColor(GX_TEVREG0,GXColor{0,0,0,255});
    GXSetTevColorIn(GX_TEVSTAGE0,GX_CC_ZERO,GX_CC_ZERO,GX_CC_ZERO,GX_CC_C0);
    GXSetTevAlphaIn(GX_TEVSTAGE0,GX_CA_ZERO,GX_CA_ZERO,GX_CA_ZERO,GX_CA_A0);
  } else if (scene==RendererScene::ZeroBrightnessLight) {
    GXLightObj light{};
    GXInitLightPos(&light,0,0,10); GXInitLightDir(&light,0,0,-1);
    GXInitLightColor(&light,GXColor{255,255,255,255});
    GXInitLightAttn(&light,1,0,0,1,0,0);
    GXInitLightDistAttn(&light,0,0,GX_DA_GENTLE);
    GXLoadLightObjImm(&light,GX_LIGHT0);
    GXSetChanMatColor(GX_COLOR0A0,GXColor{255,255,255,255});
    GXSetChanAmbColor(GX_COLOR0A0,GXColor{0,0,0,0});
    GXSetChanCtrl(GX_COLOR0A0,GX_ENABLE,GX_SRC_REG,GX_SRC_REG,GX_LIGHT0,GX_DF_NONE,GX_AF_SPOT);
    GXSetTevOp(GX_TEVSTAGE0,GX_PASSCLR);
  }
  GXBegin(scene==RendererScene::QuadTriangle ? GX_QUADS : GX_TRIANGLES,GX_VTXFMT0,3);
  GXPosition3f32(white ? -1.f : -.8f,white ? -1.f : -.7f,-.5f); if (scene==RendererScene::LitSrtg) GXColor4u8(0,0,0,255); else GXColor4u8(255,white ? 255 : 0,white ? 255 : 0,255);
  if (white) GXTexCoord2f32(0,0);
  GXPosition3f32(white ? 3.f : .8f,white ? -1.f : -.7f,-.5f); if (scene==RendererScene::LitSrtg) GXColor4u8(0,0,0,255); else GXColor4u8(white ? 255 : 0,255,white ? 255 : 0,255);
  if (white) GXTexCoord2f32(2,0);
  GXPosition3f32(white ? -1.f : 0,white ? 3.f : .8f,-.5f); if (scene==RendererScene::LitSrtg) GXColor4u8(0,0,0,255); else GXColor4u8(white ? 255 : 0,white ? 255 : 0,255,255);
  if (white) GXTexCoord2f32(0,2);
  GXEnd();
}
