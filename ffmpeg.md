Build FFmpeg with NDI support
=============================

Install dependencies:
```bash
sudo apt install build-essential cmake autoconf nasm yasm wget \
 libass-dev libvorbis-dev libx264-dev libx265-dev libsdl2-dev
```

Download ffmpeg and extract to ffmpeg folder:

`tar -xf ffmpeg-6.1.tar.gz`

Switch to ffmpeg folder:

`cd ffmpeg-6.1`

Download NDI SDK and extract it:

``tar -xf Install_NDI_SDK_v6_Linux.tar.gz`` 

Run installer:
``./Install_NDI_SDK_v6_Linux.sh``

Move ./bin and ./include folders from NDI SDK

```bash
mkdir ndi
mkdir ndi/{bin,lib}
cp NDI\ SDK\ for\ Linux/bin/x86_64-linux-gnu/* ndi/bin
cp NDI\ SDK\ for\ Linux/lib/x86_64-linux-gnu/* ndi/lib
cp -r NDI\ SDK\ for\ Linux/include ndi
```

Install NDI lib to system:

``sudo cp ndi/lib/libndi.so.6 /usr/lib``

Apply patch to `libavcodec/x86/mathops.h` file:

``patch < ../ffmpeg-patches/patch-avcodecs-mathops.patch``

Build FFmpeg:
```bash
mkdir build
PREFIX=`pwd`
PKG_CONFIG_PATH="$PREFIX/lib/pkgconfig" \
  ./configure --prefix="$PREFIX/build" \
  --extra-cflags="-I$PREFIX/build/include -I$PREFIX/ndi/include" \
  --extra-ldflags="-L$PREFIX/build/lib -L$PREFIX/ndi/lib" \
  --extra-libs="-lpthread -lm" --enable-gpl \
  --enable-libass --enable-libfreetype --enable-libvorbis --enable-libx264 \
  --enable-ffplay \
  --enable-libndi_newtek --enable-nonfree --enable-postproc --enable-pthreads
make -j 8
```

