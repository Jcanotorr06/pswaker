// Maintainer-only narrow setups. No menu process, story replay or save access.
#include "JSystem/J2DGraph/J2DPicture.h"
#include "JSystem/J2DGraph/J2DOrthoGraph.h"
#include "JSystem/J3DGraphBase/J3DTexture.h"
#include "JSystem/JKernel/JKRDecomp.h"

static std::vector<ActorState> presentation_states(const char* scenario) {
  if (!strcmp(scenario, "menu-picture-colors-v1")) {
    auto* archive = JKRArchive::mount("/res/Msg/clctres.arc", JKRArchive::MOUNT_MEM,
                                    JKRHeap::getCurrentHeap(), JKRArchive::MOUNT_DIRECTION_HEAD);
    check(archive, "mount native menu archive");
    auto* image = static_cast<ResTIMG*>(archive->getResource('TIMG', "heart_piece_base.bti"));
    check(image, "load native menu picture");
    // The ordinary menu uses an ARAM archive, which expands individual files.
    // This isolated MEM mount uses the same game decoder directly, without a
    // DVD/decompression thread or a running menu process.
    if (JKRDecomp::checkCompressed(reinterpret_cast<u8*>(image)) != COMPRESSION_NONE) {
      const auto size = archive->getExpandedResSize(image);
      check(size >= sizeof(ResTIMG) && size <= 0x100000, "bounded menu texture expansion");
      auto* expanded = static_cast<u8*>(JKRHeap::alloc(size, 32, nullptr));
      check(expanded, "allocate expanded menu texture");
      JKRDecomp::decode(reinterpret_cast<u8*>(image), expanded, size, 0);
      image = reinterpret_cast<ResTIMG*>(expanded);
    }
    auto* picture = new J2DPicture(image);
    auto draw = [=](bool tint, u8 alpha) {
      J2DOrthoGraph port(0, 0, 640, 480, -1, 1);
      port.setPort();
      picture->setBlackWhite(tint ? JUtility::TColor(90, 90, 90, 255) : JUtility::TColor(0, 0, 0, 0),
                            tint ? JUtility::TColor(200, 200, 200, 255) : JUtility::TColor(255, 255, 255, 255));
      picture->setAlpha(alpha);
      picture->draw(100, 100, 64, 64, false, false, false);
    };
    return {{"plain", [=] { draw(false, 255); }}, {"tinted", [=] { draw(true, 255); }},
            {"faded", [=] { draw(true, 128); }}, {"plain-repeated", [=] { draw(false, 255); }}};
  }
  if (!strcmp(scenario, "cutscene-fade-v1")) {
    auto draw = [](u8 color, float speed) {
      GXColor tint{color, color, color, 255};
      mDoGph_gInf_c::fadeOut(speed, tint);
      mDoGph_gInf_c::calcFade();
    };
    return {{"black-half", [=] { draw(0, 0.5f); }}, {"black-full", [=] { draw(0, 1.0f); }},
            {"white-half", [=] { draw(255, 0.5f); }}, {"black-half-repeated", [=] { draw(0, 0.5f); }}};
  }
  load_object("Link");
  auto* data = static_cast<J3DModelData*>(dComIfG_getObjectRes("Link", dRes_INDEX_LINK_BDL_CL_e));
  check(data, "load Link clothes model");
  auto* texture = data->getTexture();
  unsigned slot = 0, seen = 0;
  for (; slot < texture->getNum(); ++slot)
    if (!strcmp(data->getTextureName()->getName(slot), "linktexS3TC") && ++seen == 2) break;
  check(slot < texture->getNum(), "second Link clothes texture header required");
  auto* casual = static_cast<ResTIMG*>(dComIfG_getObjectRes("Link", dRes_INDEX_LINK_BTI_LINKTEXBCI4_e));
  check(casual, "load casual paletted texture");
  const ResTIMG hero = *texture->getResTIMG(slot);
  auto* model = mDoExt_J3DModel__create(data, 0x00080000, 0x37221222);
  check(model, "create Link model with actual player flags");
  auto draw = [=](bool alternate) {
    if (alternate) texture->setResTIMG(slot, *casual);
    else {
      *texture->getResTIMG(slot) = hero;
      texture->resTIMGChanged(texture->getResTIMG(slot));
    }
    scene_world();
    mDoExt_modelUpdateDL(model);
  };
  return {{"hero", [=] { draw(false); }}, {"casual", [=] { draw(true); }},
          {"hero-repeated", [=] { draw(false); }}};
}
