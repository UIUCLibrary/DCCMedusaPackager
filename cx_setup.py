import os
import pytest
from setuptools.config import read_configuration
from cx_Freeze import setup, Executable
import MedusaPackager
import platform



def get_project_metadata():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "setup.cfg"))
    return read_configuration(path)["metadata"]
# import imgvalidator
metadata = get_project_metadata()

def create_msi_tablename(python_name, fullname):
    shortname = python_name[:6].replace("_", "").upper()
    longname = fullname
    return "{}|{}".format(shortname, longname)


EXECUTABLE_NAME = "packagemedusa"

directory_table = [
    (
        "ProgramMenuFolder",  # Directory
        "TARGETDIR",  # Directory_parent
        "PMenu|Programs",  # DefaultDir
    ),
    (
        "PMenu",  # Directory
        "ProgramMenuFolder",  # Directory_parent
        create_msi_tablename(MedusaPackager.__title__, MedusaPackager.FULL_TITLE)
    ),
]
shortcut_table = [
    (
        "startmenuShortcutDoc",  # Shortcut
        "PMenu",  # Directory_
        "{} Documentation".format(create_msi_tablename(MedusaPackager.__title__, MedusaPackager.FULL_TITLE)),
        "TARGETDIR",  # Component_
        "[TARGETDIR]documentation.url",  # Target
        None,  # Arguments
        None,  # Description
        None,  # Hotkey
        None,  # Icon
        None,  # IconIndex
        None,  # ShowCmd
        'TARGETDIR'  # WkDir
    ),
]

INCLUDE_FILES = [
    "documentation.url"
]
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
MSVC = os.path.join(PYTHON_INSTALL_DIR, 'vcruntime140.dll')

if os.path.exists(MSVC):
    INCLUDE_FILES.append(MSVC)

build_exe_options = {
    "includes":        pytest.freeze_includes(),
    "include_msvcr": True,
    "include_files": INCLUDE_FILES,
    "packages": [
        "os",
        'pytest',
        "packaging",
        "six",
        "appdirs",
        "unittest",
        "unittest.mock",
        # # "tests",
        "MedusaPackager"
    ],
    "excludes": ["tkinter"],
}
setup(
    name=metadata["name"],
    description=metadata["description"],
    version=metadata["version"],
    author=metadata["author"],
    author_email=metadata["author_email"],
    packages=[
        'MedusaPackager',
    ],
    url=MedusaPackager.__url__,
    executables={
        Executable("MedusaPackager/__main__.py",
                   targetName=("{}.exe".format(EXECUTABLE_NAME) if platform.system() == "Windows" else EXECUTABLE_NAME))

    },
    options={"build_exe": build_exe_options,
        "bdist_msi": {
            "upgrade_code": "146B1585-F0FB-4212-87D6-E19C4EE38FB4",
            "data": {
                "Shortcut": shortcut_table,
                "Directory": directory_table
            }
        }
    },

)
