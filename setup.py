import os
import re
import shutil
import subprocess
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        super().__init__(name, sources=[])
        self.sourcedir = os.fspath(Path(sourcedir).resolve())


class BuildCMake(build_ext):
    def run(self):
        for ext in self.extensions:
            self.build_cmake(ext)

    def build_cmake(self, ext):
        cwd = os.getcwd()
        build_temp = os.path.join(cwd, self.build_temp)
        os.makedirs(build_temp, exist_ok=True)
        print("making the dir")
        os.makedirs(self.build_lib, exist_ok=True)

        cmake_args = ["cmake", "-DPYTHON=ON", ext.sourcedir]
        build_args = ["--config", "Release", "--", "-j4"]

        os.chdir(build_temp)
        self.spawn(cmake_args)
        if not self.dry_run:
            subprocess.check_call(["cmake", "--build", "."] + build_args)
        os.chdir(cwd)

        regex = re.compile(r"python3_\d+")
        for dir in [f.name for f in os.scandir(build_temp) if f.is_dir()]:
            if regex.match(dir):
                # Copy the generated imath.so to site-packages
                imath_result = shutil.copy(
                    os.path.join(build_temp, dir, "imath.so"), self.build_lib
                )
                if not Path(imath_result).is_file():
                    raise ValueError(f"unable to find {imath_result}, check if you have boost python installed")
                imathnumpy_result = shutil.copy(
                    os.path.join(build_temp, dir, "imathnumpy.so"), self.build_lib
                )
                if not Path(imathnumpy_result).is_file():
                    raise ValueError(f"unable to find {imathnumpy_result}, check if you have numpy headers installed")

setup(
    name="imath",
    version="3.1.9",
    ext_modules=[CMakeExtension("imath")],
    cmdclass=dict(build_ext=BuildCMake),
)
