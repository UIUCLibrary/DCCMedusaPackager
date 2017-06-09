from cx_Freeze import setup, Executable
import MedusaPackager
import platform


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

setup(
    name=MedusaPackager.__title__,
    version=MedusaPackager.__version__,
    packages=[
        'MedusaPackager',
    ],
    url=MedusaPackager.__url__,
    description=MedusaPackager.__description__,
    executables={
        Executable("MedusaPackager/processcli.py",
                   targetName=("{}.exe".format(EXECUTABLE_NAME) if platform.system() == "Windows" else EXECUTABLE_NAME))

    },
    options={"build_exe": {
        "include_msvcr": True
    }
    },

)
