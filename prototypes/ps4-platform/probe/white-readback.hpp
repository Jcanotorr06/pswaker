// Shared known-result check: exact RGBA white, never a relaxed RGB-only check.
bool white_snapshot(const wgpu::Texture& texture,const char* name) {
  checkpoint(name);
  if (!texture) { note("TEXTURE %s missing",name); return verdict(false,name); }
  note("TEXTURE %s width=%u height=%u format=%u",name,texture.GetWidth(),texture.GetHeight(),unsigned(texture.GetFormat()));
  // White has the same exact bytes in either supported four-channel layout.
  if (texture.GetWidth()<32 || texture.GetHeight()<32 ||
      (texture.GetFormat()!=wgpu::TextureFormat::RGBA8Unorm && texture.GetFormat()!=wgpu::TextureFormat::BGRA8Unorm))
    return verdict(false,name);
  auto encoder=aurora::webgpu::g_device.CreateCommandEncoder();
  wgpu::BufferDescriptor descriptor{};
  descriptor.usage=wgpu::BufferUsage::CopyDst|wgpu::BufferUsage::MapRead; descriptor.size=256*32;
  auto buffer=aurora::webgpu::g_device.CreateBuffer(&descriptor);
  wgpu::TexelCopyTextureInfo source{}; source.texture=texture;
  wgpu::TexelCopyBufferInfo target{}; target.buffer=buffer; target.layout.bytesPerRow=256; target.layout.rowsPerImage=32;
  const wgpu::Extent3D size{32,32,1}; encoder.CopyTextureToBuffer(&source,&target,&size);
  auto commands=encoder.Finish(); aurora::webgpu::g_queue.Submit(1,&commands);
  auto done=std::make_shared<std::atomic<int>>(0);
  buffer.MapAsync(wgpu::MapMode::Read,0,256*32,wgpu::CallbackMode::AllowSpontaneous,
    [done,name](wgpu::MapAsyncStatus status,wgpu::StringView message) {
      note("MAP %s status=%u message=%.*s",name,unsigned(status),int(std::min(message.length,size_t(512))),message.data ? message.data : "");
      done->store(status==wgpu::MapAsyncStatus::Success ? 1 : -1);
    });
  const auto until=std::chrono::steady_clock::now()+std::chrono::seconds(5);
  while (*done==0 && std::chrono::steady_clock::now()<until) {
    aurora::webgpu::g_instance.ProcessEvents(); std::this_thread::sleep_for(std::chrono::milliseconds(1));
  }
  if (*done!=1) {
    note("READBACK %s completion=%d (0=timeout,-1=map-failure); pixel comparison not performed",name,done->load());
    buffer.Destroy(); return verdict(false,name);
  }
  const auto* pixels=static_cast<const uint8_t*>(buffer.GetConstMappedRange());
  bool pass=pixels!=nullptr;
  unsigned mismatches=0;
  if (pixels) {
    for (unsigned y=0;y<32;++y) for (unsigned x=0;x<32;++x) {
      const auto* p=pixels+y*256+x*4;
      if (p[0]!=255 || p[1]!=255 || p[2]!=255 || p[3]!=255) {
        if (!mismatches) note("MISMATCH %s xy=%u,%u actual=%u,%u,%u,%u expected=255,255,255,255",name,x,y,p[0],p[1],p[2],p[3]);
        ++mismatches;
      }
    }
    note("PIXEL %s first=%u,%u,%u,%u expected=255,255,255,255 mismatches=%u/1024",name,pixels[0],pixels[1],pixels[2],pixels[3],mismatches);
    pass &= mismatches==0;
  } else note("READBACK %s mapped-range=null; pixel comparison not performed",name);
  buffer.Unmap(); return verdict(pass,name);
}
