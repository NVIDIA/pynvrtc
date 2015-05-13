# Copyright (c) 2014-2015, NVIDIA Corporation.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from .interface import NVRTCException, NVRTCInterface

class ProgramException(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.get_message()

    def get_message(self):
        return self._msg


class Program(object):
    """
    An NVRTC program object.

    This is a high-level wrapper around the NVRTC program API.
    """

    def __init__(self,
                 src, name="default_program",
                 headers=[], include_names=[],
                 lib_name=''):
        self._interface = NVRTCInterface(lib_name)
        self._program = self._interface.nvrtcCreateProgram(src, name,
                                                           headers,
                                                           include_names)

    def __del__(self):
        if hasattr(self, '_interface'):
            self._interface.nvrtcDestroyProgram(self._program)

    def compile(self, options=[]):
        """
        Compiles the program object to PTX using the compiler options
        specified in `options`.
        """
        try:
            self._interface.nvrtcCompileProgram(self._program, options)
            ptx = self._interface.nvrtcGetPTX(self._program)
            return ptx
        except NVRTCException as e:
            log = self._interface.nvrtcGetProgramLog(self._program)
            raise ProgramException(log)
