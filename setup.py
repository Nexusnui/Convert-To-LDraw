from setuptools import setup

setup(
    name='ConvertToLDraw',
    version='1.3.0',
    description='This is a graphical Python program for converting various 3D file formats(stl,3mf,obj,stp, etc.) to the LDraw file format (.dat).',
    url='https://github.com/Nexusnui/Convert-To-LDraw',
    author='Nexusnui',
    author_email='nocontact@notaprovider.de',
    license='GPL 3.0',
    packages=['ConvertToLDraw',
              'ConvertToLDraw.brick_data',
              'ConvertToLDraw.icons',
              'ConvertToLDraw.ui_elements',
              'colorpicker',
              'ConvertToLDraw.ui_elements.js-libraries'
              ],
    package_data={
        'ConvertToLDraw.brick_data': ['colour_definitions.csv'],
        'ConvertToLDraw.icons': ['ConvertToLDraw_icon.ico', 'ConvertToLDraw_icon*.png', 'reload-icon.svg'],
        'ConvertToLDraw.ui_elements': ['viewer_template.html'],
        'ConvertToLDraw.ui_elements.js-libraries': ['*']
    },
    install_requires=["numpy==2.2.3",
                      "cascadio==0.0.16",
                      "charset-normalizer==3.4.1",
                      "lxml==5.3.1",
                      "manifold3d==3.0.1",
                      "meshio==5.3.5",
                      "networkx==3.4.2",
                      "pillow==11.1.0",
                      "pycollada==0.9",
                      "PyQt6==6.8.1",
                      "PyQt6-WebEngine==6.8.0",
                      "scipy==1.15.2",
                      "trimesh==4.6.3",
                      ],
    entry_points={
        'gui_scripts': [
            'ConvertToLDraw = ConvertToLDraw.app:run',
        ]
    },

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3.12',
    ],
)
