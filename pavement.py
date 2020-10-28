#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# Do not change the previous lines. See PEP 8, PEP 263.
#
from paver.easy import *
from paver.setuputils import setup
import urllib.request
import os
import platform

setup(
    name="TestProject",
    packages=[],
    version="1.0",
    url="http://example.com/",
    author="Davide Romanini",
    author_email="davide.romanini@gmail.com")


@task
def libunrar():
    if platform.system() == "Windows":
        UNRAR_SRC = "http://www.rarlab.com/rar/UnRARDLL.exe"
    else:
        UNRAR_SRC = "http://www.rarlab.com/rar/unrarsrc-5.3.2.tar.gz"

    dest = "libunrar/" + os.path.basename(UNRAR_SRC)

    if not os.path.exists(dest):
        print("Fetching " + UNRAR_SRC + "...")
        urllib.request.urlretrieve(UNRAR_SRC, dest)

    if platform.system() == "Windows":
        print("Please extract UnRAR.dll from UnRARDLL.exe into libunrar/libunrar.so")
    else:
        if not os.path.exists("libunrar/unrar"):
            print("Unpacking " + dest + "...")
            sh("tar xfz %s -C libunrar" % dest)
        print("Compiling unrar...")
        sh("cd libunrar/unrar && make lib")
        sh("cp libunrar/unrar/libunrar.so libunrar/libunrar.so")
        print("Cleaning up ...")
        sh("rm -rf libunrar/unrar*")
        sh("rm -f libunrar/unrar/libunrar.so")


@task
@needs(["distutils.command.sdist"])
def sdist():
    """Generate docs and source distribution."""
    pass
