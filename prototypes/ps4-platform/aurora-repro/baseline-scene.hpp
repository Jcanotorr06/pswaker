// Verbatim triangle function from failed diagnostic revision 605d57a.
void triangle(bool white=false,unsigned width=1280,unsigned height=720) {
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
    GXLoadTexObj(&texture,GX_TEXMAP0);
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
  GXBegin(GX_TRIANGLES,GX_VTXFMT0,3);
  GXPosition3f32(white ? -1.f : -.8f,white ? -1.f : -.7f,-.5f); GXColor4u8(255,white ? 255 : 0,white ? 255 : 0,255);
  if (white) GXTexCoord2f32(0,0);
  GXPosition3f32(white ? 3.f : .8f,white ? -1.f : -.7f,-.5f); GXColor4u8(white ? 255 : 0,255,white ? 255 : 0,255);
  if (white) GXTexCoord2f32(2,0);
  GXPosition3f32(white ? -1.f : 0,white ? 3.f : .8f,-.5f); GXColor4u8(white ? 255 : 0,white ? 255 : 0,255,255);
  if (white) GXTexCoord2f32(0,2);
  GXEnd();
}
