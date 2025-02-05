from setuptools import setup

setup(
    name='ConvertToLDraw',
    version='1.1.1',
    description='This is a graphical Python program for converting various 3D file formats(stl,3mf,obj,stp, etc.) to the LDraw file format (.dat).',
    url='https://github.com/Nexusnui/Convert-To-LDraw',
    author='Nexusnui',
    author_email='nocontact@notaprovider.de',
    license='GPL 3.0',
    packages=['ConvertToLDraw', 'ConvertToLDraw.brick_data', 'ConvertToLDraw.icons'],
    package_data={
        'ConvertToLDraw.brick_data': ['*'],
        'ConvertToLDraw.icons': ['ConvertToLDraw_icon.ico', 'reload-icon.svg']
    },
    install_requires=["numpy==2.2.2",
                      "cascadio==0.0.15",
                      "chardet==5.2.0",
                      "lxml==5.3.0",
                      "manifold3d==3.0.1",
                      "meshio==5.3.5",
                      "networkx==3.4.2",
                      "pillow==11.1.0",
                      "pycollada==0.8",
                      "pyglet==1.5.29",
                      "PyQt6==6.8.0",
                      "scipy==1.15.1",
                      "trimesh==4.6.1",
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3.12',
    ],
)
