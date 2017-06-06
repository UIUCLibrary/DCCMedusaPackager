from cx_Freeze import setup, Executable
import MedusaPackager
import platform

EXECUTABLE_NAME = "packagemedusa"

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
