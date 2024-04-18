
## Play NDI command
```bash
/usr/local/bin/ffplay -fs -alwaysontop -fflags nobuffer -sync ext -f libndi_newtek -bandwidth 0 -i "PETRLE (Proclaim - NDI-Monitor)"
```

Quality: `bandwith` 0 - high, 1 - low

## Build FFMPEG with NDI support
Project FFMPEG-NDI: https://github.com/lplassman/FFMPEG-NDI 
or custom build in