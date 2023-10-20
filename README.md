![Image of Custom Part](icons/stlToLDraw_icon.png)

This is a simple graphical Python program for converting a 3D printing [.stl](https://en.wikipedia.org/wiki/STL_%28file_format%29)
files to LDraw format [.dat](http://www.ldraw.org/article/218) files. Then you can use the part just like any other part in
your favorite LDraw viewer or CAD program.

The Graphical Userinterface:
![Screenshot of the GUI](graphical_userinterface.png)

When the input file is selected first the output file will have the same name with a .dat extension.

Usage in commandline:

```
> python stlToDat.py input_file.stl -o output_file.dat -c ldrawcolour
```

If the output file is not specified the input file name will be used with a .dat extension.

The default colour("16") will be used if not specified. 
Check the official LDraw Colour Definition Reference for the available colour codes.
Only change the colour if you want create a multicolour part or if you want to use a html colour["0x2hexcolour"], that is not available as a LDraw colour.



The STL file needs to be in millimeters.

This program has the following dependencies:
- numpy-stl
- customtkinter(only if you use the graphical user interface)

Run/Install:

Currently there is only a Windows Version.
Under Releases you find the current version as zip archive.
Unpack the contained directory a save it at a convenient location.
To launch the program open the ".exe" file in the directory.
If have an anti-virus software installed it might warn you.

Mac and Linux users have to setup a python environment with the required with dependencies.

This a fork of a [python script of Hazen Babcock](https://github.com/HazenBabcock/stl-to-dat).
These changes that where made:
- load mesh with numpy-stl for compatability with binary stl files
- set colour of the output file
- simple graphical user interface was added for easier use



Since the program now loads the mesh, more functionality for simplification or repair of the mesh could be added.