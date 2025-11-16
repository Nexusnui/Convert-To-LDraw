from setuptools import setup

setup(
    name='3DToLD',
    version='1.6.0',
    description='This is a graphical Python program for converting various 3D file formats(stl,3mf,obj,stp, etc.) to the LDraw file format (.dat).',
    url='https://github.com/Nexusnui/Convert-To-LDraw',
    author='Nexusnui',
    author_email='developer@nexusnui.de',
    license='GPL 3.0',
    packages=['ThreeDToLD',
              'ThreeDToLD.brick_data',
              'ThreeDToLD.icons',
              'ThreeDToLD.ui_elements',
              'ThreeDToLD.model_loaders',
              'colorpicker',
              'ThreeDToLD.ui_elements.js-libraries'
              ],
    package_data={
        'ThreeDToLD.brick_data': ['colour_definitions.csv'],
        'ThreeDToLD.icons': ['3DToLD_icon.ico', '3DToLD_icon*.png',
                                 'reload-icon.svg', 'loading_animation.webm',
                                 'Loading_Symbol.png'],
        'ThreeDToLD.ui_elements': ['viewer_template.html'],
        'ThreeDToLD.ui_elements.js-libraries': ['*']
    },
    install_requires=["numpy>=2.2.0,<=2.3.2",
                      "cascadio==0.0.16",
                      "charset-normalizer==3.4.3",
                      "lxml==6.0.2",
                      "manifold3d==3.2.1",
                      "meshio==5.3.5",
                      "networkx>=3.4,<=3.5",
                      "pillow==11.3.0",
                      "pycollada==0.9.2",
                      "PyQt6==6.10.0",
                      "PyQt6-WebEngine==6.10.0",
                      "scipy>=1.15.0,<=1.16.1",
                      "trimesh==4.8.3",
                      ],
    entry_points={
        'gui_scripts': [
            '3DToLD = ThreeDToLD.app:run',
        ]
    },

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.12',
        'Natural Language :: English',
    ],
)
