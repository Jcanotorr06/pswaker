#pragma once
// Game-facing entry points of the PS4 message picture adapter. Kept free of
// port types so The Wind Waker's message code can include it directly.
#include <cstdint>

// Shows encoded GX textures (ResTIMG) on an existing picture and its optional
// shadow: `image` replaces the last texture and a non-null `partner` replaces
// texture 0, the crossfade partner of animated stick pictures. Game thread only.
using PswakerPictureApply = void (*)(void* picture, void* shadow, const void* image, const void* partner);

// After the game has set up a retained message picture: true when the adapter
// took it over as a PS4 control prompt (already applied), false to keep the
// game's own non-control picture. quarterTurns counts the picture's clockwise
// quarter turns. Control pictures are retained for refresh until destroyed.
bool pswaker_message_picture_set(void* picture, void* shadow, uint8_t pictureNo, uint8_t quarterTurns,
                                 PswakerPictureApply apply);
// After the game turns a retained picture for animation; re-applies when needed.
void pswaker_message_picture_turned(void* picture, uint8_t quarterTurns);
// From J2DPicture's destructor, or before the game puts its own texture on the
// picture (fopMsgM_blendDraw); forgets any retained pair containing it.
void pswaker_message_picture_released(void* picture);
