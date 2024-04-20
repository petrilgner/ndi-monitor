## Play NDI command
```bash
/usr/local/bin/ffplay -fs -alwaysontop -fflags nobuffer -sync ext -f libndi_newtek -bandwidth 0 -i "PETRLE (Proclaim - NDI-Monitor)"
```

Quality: `bandwith` 0 - high, 1 - low

## Build FFMPEG with NDI support
Project FFMPEG-NDI: https://github.com/lplassman/FFMPEG-NDI 
or custom build in

## Android TV Control

The app allow to control Android TV - turn on/off and select HDMI output when changing scenes. Android TV communication is based on: https://github.com/Jekso/AndroidTV-Remote-Controller

Before using the app is required to enable Development mode on TV and pair ADB debugger.

- Install Platform tools: https://dl.google.com/android/repository/platform-tools-latest-linux.zip
- Add tools to the PATH variable:
  - Edit `.profile` file and add new line: 
  
  ``export PATH=$PATH:/opt/platform-tools``
  
  - Get Android TV IP address and put it into `config/main.yaml`
  - Try using Turn On/Turn Off command - if debugging is enabled on TV, it will show confirm dialog.
    - Allow debugging and select to remember the choice.

