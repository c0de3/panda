#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as install_orig
from setuptools.command.develop import develop as develop_orig
import os
import shutil

##############################
# 1)  Populate panda/autogen #
##############################

from sys import path as sys_path
sys_path.append("utils")
from create_panda_datatypes import main as create_datatypes
create_datatypes()

################################################
# 2) Copy panda object files: libpanda-XYZ.so, #
#    pc-bios/*, and all .so files for plugins  #
################################################

# XXX - Can we toggle this depending ond if we're run as 'setup.py develop' vs 'setup.py install'
# When we're run in develop mode, we shouldn't copy the prebuild binaries and instead should
# find them in ../../build/
lib_dir = 'panda/data'
def copy_objs():
    build_root = "../../build/"

    if os.path.isdir(lib_dir):
        assert('panda' in lib_dir), "Refusing to rm -rf directory without 'panda' in it"
        shutil.rmtree(lib_dir)
    os.mkdir(lib_dir)

    # Copy bios directory
    biosdir = os.path.join(build_root, "pc-bios")
    shutil.copytree(biosdir, lib_dir+"/pc-bios")

    for arch in ['arm', 'i386', 'x86_64', 'ppc']:
        libname = "libpanda-"+arch+".so"
        softmmu = arch+"-softmmu"
        path = os.path.join(*[build_root, softmmu, libname])
        plugindir = os.path.join(*[build_root, softmmu, "panda", "plugins"])
        plog = os.path.join(*[build_root, softmmu, "plog_pb2.py"])
        os.mkdir(os.path.join(lib_dir, softmmu))

        assert (os.path.isfile(path)), "Missing file {} - did you run build.sh from panda/build directory?".format(path)
        shutil.copy(    plog,       os.path.join(lib_dir, softmmu, "plog_pb2.py"))
        shutil.copy(    path,       os.path.join(lib_dir, softmmu))
        shutil.copytree(plugindir,  os.path.join(lib_dir, softmmu, "libpanda-"+arch))

#########################
# 3)  Build the package #
#########################

from setuptools.command.install import install as install_orig
from setuptools.command.develop import develop as develop_orig
class custom_develop(develop_orig):
    def run(self):
        # Delete panda/data in the case of `setup.py develop`
        if os.path.isdir(lib_dir):
            assert('panda' in lib_dir), "Refusing to rm -rf directory without 'panda' in it"
            shutil.rmtree(lib_dir)
        super().run()

class custom_install(install_orig):
    # Run copy_objs before we install in the case of `setup.py install`
    def run(self):
        copy_objs()
        super().run()


setup(name='panda',
      version='0.1',
      description='Python Interface to Panda',
      author='Andrew Fasano, Luke Craig, and Tim Leek',
      author_email='fasano@mit.edu',
      url='https://github.com/panda-re/panda/',
      packages=['panda', 'panda.taint', 'panda.autogen',
                'panda.images', 'panda.arm', 'panda.x86'],
      package_data = { 'panda': ['data/**/*'] },
      install_requires=[ 'cffi', 'colorama', 'protobuf'],
      python_requires='>=3.5',
      cmdclass={'install': custom_install, 'develop': custom_develop}
     )