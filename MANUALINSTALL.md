# Todo Rewrite for 1.1.0
# Manual Installation (Windows/Mac/Linux)
This guide is mainly written for Windows.  
The parts for Mac and Linux are incomplete.
Prerequisite:
- Python is installed (tested with 3.12.0)

Installation:
1. Download the latest Source code Archive(zip or tar.gz)  
https://github.com/Nexusnui/Convert-To-LDraw/releases/latest  
2. Create a directory named "ConvertToLDraw" in a appropriate location  
3. The archive contains one folder move the contents of that folder into your "ConvertToLDraw" directory  
4. Open/Goto your "ConvertToLDraw" in the terminal/commandline prompt  
5. Create virtual python environment with `python -m venv venv`
6. Activate the environment:
   - `venv\Scripts\activate`(Windows Command Prompt)
   - `.\venv\Scripts\activate`(Windows PowerShell)
   - `venv/bin/activate`(Mac/Linux)
   - [other variants](https://docs.python.org/3/library/venv.html#how-venvs-work)
7. Install requirements with `pip install -r build-scripts/requirements.txt`
8. Try to open the application with `python ConvertToLDraw/app.py` if it opens everything went right
9. close the application and deactivate the virtual Environment with `deactivate`

Creating a Shortcut(Windows)
1. Open your "ConvertToLDraw" directory in file explorer
2. Goto venv\Scripts
3. Copy the full path of "pythonw.exe"
4. Fo back to the "ConvertToLDraw" directory
5. Click on "new" and "shortcut"
6. Paste the path of pythonw.exe (remove quotation marks if there are any)
7. Click next
8. Name the shortcut "ConvertToLDraw"
9. Right click the new shortcut and select "properties"
10. Remove "\venv\Scripts" from the execute in field
11. Add "ConvertToLDraw/app.py" after target -> "...\pythonw.exe ConvertToLDraw/app.py"
12. Optionally change the icon to the one in ConvertToLDraw\icons
13. Save the changes
14. You can now open the application by double clicking the shortcut

Creating a Shortcut(Mac/Linux):
- You need to create a link to your "venv/bin/pythonw" opening "ConvertToLDraw/app.py" running in the "ConvertToLDraw" directory
- On Linux you can manually create a .desktop file in the appropriate location
- Otherwise you might want try [pyshortcuts](https://newville.github.io/pyshortcuts/)