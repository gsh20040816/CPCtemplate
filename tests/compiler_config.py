"""Use the caller's compiler, or discover GNU C++ on either supported platform."""
import os
import shutil

CXX = os.environ.get('CXX') or shutil.which('g++-16') or shutil.which('g++')
if not CXX:
    raise RuntimeError('No C++ compiler found; install g++ or set CXX')
