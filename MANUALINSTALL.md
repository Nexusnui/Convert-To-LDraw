# Manual Installation (Windows/Linux/Mac)
This guide was tested on Windows(11,x86) and Linux(Mint, Fedora KDE),
the installation with pipx should also work on Mac(not fully functional see known issues).

Prerequisites:
- Python is installed (tested with 3.13.0[Fedora], 3.12.0[Windows] and 3.10.12[Mint])
- pip is installed (on some Linux Distros it is not installed with Python)
- pipx is installed (+ ensurepath activated)

Installation:  
1. installation with pipx through console/terminal:  
`pipx install https://github.com/Nexusnui/Convert-To-LDraw/releases/latest/download/3dtold.tar.gz`  
or like this:  
`python -m pipx install https://github.com/Nexusnui/Convert-To-LDraw/releases/latest/download/3dtold.tar.gz`
or on some Linux Distro like this:  
`python3 -m pipx install https://github.com/Nexusnui/Convert-To-LDraw/releases/latest/download/3dtold.tar.gz`
2. You can now run it by with typing `3DToLD`

Update:  
For updating use the installation command and append `--force` to it.

Troubleshooting:  
If you run `3DToLD` and it is not found you may have "ensurepath" not enabled.
Fix it with:  
`pipx ensurepath`  
or on some Linux distros:  
`python3 -m pipx ensurepath`  
If you are on an Ubuntu based Linux distro and see an error message like this:  
`qt.qpa.plugin: From 6.5.0 xcb-cursor0 or libxcb-cursor0 is needed to load the Qt xcb platform plugin`  
Install libxcb-cursor0 with:  
`sudo apt install libxcb-cursor0`  

Creating a Shortcut(Windows)
1. Open the folder you want to create the shortcut in.
2. Click on "new" and "shortcut"
3. Type in "3DToLD"
4. Click next
5. Name the shortcut "3DToLD"  

Optional Steps:  
6. Right-click the new shortcut and select "properties"
7. Change target to the location your projects are located for example "C:\Users\{YourUserName}\3D Objects"
8. Optionally change the icon to the one in
"C:\Users\{YourUserName}\pipx\venvs\3dtold\Lib\site-packages\ThreeDToLD\icons\"
or [downloadable here](https://github.com/Nexusnui/Convert-To-LDraw/raw/master/ThreeDToLD/icons/3DToLD_icon.ico).


Use the .desktop file on Linux:  
1. [Download the Icon](https://github.com/Nexusnui/Convert-To-LDraw/raw/master/ThreeDToLD/icons/3DToLD_icon_256x256.png)
and move it to "~/.local/share/icons" (you may need to create that one) or another appropriate location for icons.
2. [Download ConvertToLDraw.desktop](https://github.com/Nexusnui/Convert-To-LDraw/raw/master/build-stuff/3DToLD.desktop) and move it to "~/.local/share/applications"
or another appropriate location for .desktop files.
3. Make sure the .desktop file has the appropriate permissions to be executable


Alias on Mac:
- pipx creates an alias in  "/Users/{YourUserName}/.local/bin/"
- you can copy or create another alias to in your application folder
- icons can be found [here](ThreeDToLD/icons)