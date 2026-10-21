#!/usr/bin/env python3
"""Build a startup isolation package with the already prepared selected runtime."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess

HERE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(command, log, **kwargs):
    with log.open('w') as stream:
        subprocess.run(command, check=True, stdout=stream, stderr=subprocess.STDOUT, **kwargs)

def identity(root):
    paths = [p for p in HERE.iterdir() if p.suffix in {'.c','.cpp','.py','.sh','.txt'}]
    paths += [HERE/'../runtime-preflight/main.cpp', HERE/'../sdk.lock.json',
              HERE/'../sources.lock.json', HERE/'../adapt-platform.py']
    sources = {os.path.relpath(p, HERE):sha(p) for p in sorted(paths)}
    libraries = {p.name:sha(p) for p in (root/'sysroot/lib').glob('*.a')}
    versions = {name:subprocess.check_output(command,text=True).strip() for name,command in {
        'clang':['clang-21','--version'], 'cmake':['cmake','--version'],
        'ninja':['ninja','--version'], 'dotnet':['dotnet','--version']}.items()}
    value = {'files':sources, 'runtime_archives':libraries, 'host_tools':versions}
    return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()[:20],value

def sfo_fields(path):
    raw = path.read_bytes()
    assert raw[:4] == b'\0PSF'
    keys, data, count = struct.unpack_from('<III', raw, 8)
    result = {}
    for i in range(count):
        key, kind, length, _, offset = struct.unpack_from('<HHIII',raw,20+i*16)
        name = raw[keys+key:].split(b'\0',1)[0].decode()
        value = raw[data+offset:][:length]
        result[name] = int.from_bytes(value,'little') if kind == 0x404 else value.rstrip(b'\0').decode()
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    root = parser.parse_args().root.resolve()
    evidence = root/'startup-evidence'
    evidence.mkdir(exist_ok=True)
    sdk = root/'sdk/opt/pacbrew/ps4/openorbis'
    dolphin = root/'refs/DolphinPS4'
    env = dict(os.environ, OPENORBIS=str(sdk), OO_PS4_TOOLCHAIN=str(sdk),
        PS4_SYSROOT=str(root/'sysroot'), PSB=str(root), DOLPHINPS4=str(dolphin),
        DOTNET_CLI_TELEMETRY_OPTOUT='1', DOTNET_NOLOGO='1',
        DOTNET_SYSTEM_GLOBALIZATION_INVARIANT='1', NUGET_PACKAGES=str(root/'nuget-packages'))
    build_id, inputs = identity(root)
    build = root/'build/startup'
    run(['cmake','-S',str(HERE),'-B',str(build),'-G','Ninja',
        '-DCMAKE_TOOLCHAIN_FILE='+str(dolphin/'toolchain/ps4-love-modern.cmake'),
        '-DDOLPHINPS4='+str(dolphin),'-DCMAKE_BUILD_TYPE=Release',
        '-DPS4_PAID=0x3800000000000035','-DPSWAKER_STARTUP_ID='+build_id], evidence/'configure.log',env=env)
    run(['cmake','--build',str(build),'--parallel','5'], evidence/'build.log',env=env)
    early = build/'CMakeFiles/startup_probe.dir/early.c.obj'
    imports = subprocess.check_output(['llvm-nm-21','--undefined-only',str(early)],text=True)
    (evidence/'early-imports.txt').write_text(imports)
    allowed = {'sceKernelOpen','sceKernelWrite','sceKernelFsync','sceKernelClose',
               'sceKernelMkdir','sceKernelDebugOutText'}
    assert {line.split()[-1] for line in imports.splitlines() if line.split()} <= allowed, imports
    elf = build/'startup_probe'
    disassembly = subprocess.check_output(['llvm-objdump-21','-d','--disassemble-symbols=_start',str(elf)],text=True)
    (evidence/'entry-disassembly.txt').write_text(disassembly)
    assert 'pswaker_startup_entry' in disassembly and '_start_ps4_c' in disassembly
    assert disassembly.index('pswaker_startup_entry') < disassembly.index('_start_ps4_c')
    sdk_version = subprocess.check_output(['dotnet','--version'],text=True).strip()
    tool_source = root/'src/liborbispkg'
    (tool_source/'global.json').write_text(json.dumps({'sdk':{'version':sdk_version,'rollForward':'disable'}}))
    run(['dotnet','publish','PkgTool.Core/PkgTool.Core.csproj','-c','Release',
        '--self-contained','false','-p:RestorePackagesWithLockFile=true','-o',str(root/'build/pkgtool')],
        evidence/'pkgtool.log',env=env,cwd=tool_source)
    stage = root/'build/startup-stage'
    (stage/'sce_sys').mkdir(parents=True,exist_ok=True)
    eboot = build/'startup_probe_eboot/eboot.bin'
    shutil.copyfile(eboot,stage/'eboot.bin')
    shutil.copyfile(dolphin/'sce_sys/icon0.png',stage/'sce_sys/icon0.png')
    manifest = {'build_id':build_id,'scope':'Startup isolation only; no graphics/audio/pad validation',
        'inputs':inputs,'selected_source_archives':json.loads((root/'evidence/source-archives.json').read_text()),
        'sdk':json.loads((HERE/'../sdk.lock.json').read_text()),
        'adaptations':json.loads((root/'evidence/local-adaptations.json').read_text()),
        'elf_sha256':sha(elf),'eboot_sha256':sha(eboot)}
    (stage/'build-info.json').write_text(json.dumps(manifest,indent=2)+'\n')
    env.update(PS4_PKGTOOL=str(root/'build/pkgtool/PkgTool.Core'),SFO_STYLE='plain',DOLPHIN_PS4_MODULES_DIR='/nonexistent')
    output = root/'startup-out'
    run(['bash',str(dolphin/'scripts/make-pkg.sh'),str(stage),'PSWK00011',
        'PSWaker Startup Probe','01.00','PSWAKERSTARTUP01',str(output)], evidence/'package.log',env=env)
    package = output/'IV0000-PSWK00011_00-PSWAKERSTARTUP01.pkg'
    tool = str(root/'build/pkgtool/PkgTool.Core')
    extracted = evidence/'extract'
    extracted.mkdir(exist_ok=True)
    run([tool,'pkg_extract',str(package),str(extracted)],evidence/'extract.log',env=env)
    payload = extracted/'uroot'
    files = {p.relative_to(payload).as_posix():sha(p) for p in payload.rglob('*') if p.is_file()}
    assert set(files) == {'eboot.bin','build-info.json','sce_module/libc.prx',
        'sce_module/libSceFios2.prx','sce_sys/about/right.sprx','sce_sys/keystone'},files
    assert files['eboot.bin'] == manifest['eboot_sha256']
    assert build_id.encode() in elf.read_bytes()
    assert json.loads((payload/'build-info.json').read_text()) == manifest
    entries = subprocess.check_output([tool,'pkg_listentries',str(package)],env=env,text=True)
    (evidence/'package-entries.txt').write_text(entries)
    index = next(line.split()[3] for line in entries.splitlines() if line.split() and line.split()[-1]=='PARAM_SFO')
    run([tool,'pkg_extractentry',str(package),index,str(extracted/'param.sfo')],evidence/'sfo-extract.log',env=env)
    fields = sfo_fields(extracted/'param.sfo')
    assert fields['TITLE_ID']=='PSWK00011' and fields['TITLE']=='PSWaker Startup Probe'
    assert fields['APP_VER']=='01.00' and fields['CATEGORY']=='gd'
    record = {'build_id':build_id,'package':{'filename':package.name,'sha256':sha(package)},
        'elf_sha256':manifest['elf_sha256'],'eboot_sha256':manifest['eboot_sha256'],
        'package_inventory':files,'sfo':fields,'hardware_status':'Not executed on PS4; owner retry required'}
    (evidence/'artifacts.json').write_text(json.dumps(record,indent=2)+'\n')
    (evidence/'build-info.json').write_text(json.dumps(manifest,indent=2)+'\n')
    shutil.copyfile(build/'startup-crt1.S', evidence/'startup-crt1.S')
    print(json.dumps(record,indent=2))
