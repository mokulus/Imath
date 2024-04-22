import os
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

        cmake_args = ["cmake", "-DPYTHON=ON", ext.sourcedir]
        build_args = ["--config", "Release", "--", "-j4"]

        os.chdir(build_temp)
        self.spawn(cmake_args)
        if not self.dry_run:
            subprocess.check_call(["cmake", "--build", "."] + build_args)
        os.chdir(cwd)

        # Copy the generated imath.so to site-packages
        shutil.copy(os.path.join(build_temp, "python3_11/imath.so"), self.build_lib)
        shutil.copy(
            os.path.join(build_temp, "python3_11/imathnumpy.so"), self.build_lib
        )


setup(
    name="imath",
    version="3.1.9",
    ext_modules=[CMakeExtension("imath")],
    cmdclass=dict(build_ext=BuildCMake),
)
