# Copyright (c) 2014-2016, NVIDIA Corporation.  All rights reserved.
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


from ctypes import (
    POINTER,
    c_int,
    c_void_p,
    byref,
    create_string_buffer,
    c_char_p,
    c_size_t,
    sizeof,
    cdll,
)
from platform import system


# NVRTC status codes
NVRTC_SUCCESS = 0
NVRTC_ERROR_OUT_OF_MEMORY = 1
NVRTC_ERROR_PROGRAM_CREATION_FAILURE = 2
NVRTC_ERROR_INVALID_INPUT = 3
NVRTC_ERROR_INVALID_PROGRAM = 4
NVRTC_ERROR_INVALID_OPTION = 5
NVRTC_ERROR_COMPILATION = 6
NVRTC_ERROR_BUILTIN_OPERATION_FAILURE = 7


class NVRTCException(Exception):
    """
    Exception wrapper for NVRTC error codes.
    """
    def __init__(self, msg):
        Exception.__init__(self)
        self._msg = msg

    def __str__(self):
        return 'NVRTC Error: %s' % self._msg

    def __repr__(self):
        return str(self)



class NVRTCInterface(object):
    """
    Low-level interface to NVRTC.  This class is primarily designed for
    interfacing the high-level API with the NVRTC binary, but clients
    are free to use NVRTC directly through this class.
    """
    def __init__(self, lib_path=''):
        self._lib = None
        self._load_nvrtc_lib(lib_path)

    def _load_nvrtc_lib(self, lib_path):
        """
        Loads the NVRTC shared library, with an optional search path in
        lib_path.
        """
        if sizeof(c_void_p) == 8:
            if system() == 'Windows':
                def_lib_name = 'nvrtc64_80.dll'
            elif system() == 'Darwin':
                def_lib_name = 'libnvrtc.dylib'
            else:
                def_lib_name = 'libnvrtc.so'
        else:
            raise NVRTCException('NVRTC is not supported on 32-bit platforms.')

        if len(lib_path) == 0:
            name = def_lib_name
        else:
            name = lib_path

        self._lib = cdll.LoadLibrary(name)

        self._lib.nvrtcCreateProgram.argtypes = [
            POINTER(c_void_p),  # prog
            c_char_p,           # src
            c_char_p,           # name
            c_int,              # numHeaders
            POINTER(c_char_p),  # headers
            POINTER(c_char_p)   # include_names
        ]
        self._lib.nvrtcCreateProgram.restype = c_int

        self._lib.nvrtcDestroyProgram.argtypes = [
            POINTER(c_void_p)   # prog
        ]
        self._lib.nvrtcDestroyProgram.restype = c_int

        self._lib.nvrtcCompileProgram.argtypes = [
            c_void_p,           # prog
            c_int,              # numOptions
            POINTER(c_char_p)   # options
        ]
        self._lib.nvrtcCompileProgram.restype = c_int

        self._lib.nvrtcGetPTXSize.argtypes = [
            c_void_p,           # prog
            POINTER(c_size_t)   # ptxSizeRet
        ]
        self._lib.nvrtcGetPTXSize.restype = c_int

        self._lib.nvrtcGetPTX.argtypes = [
            c_void_p,           # prog
            c_char_p            # ptx
        ]
        self._lib.nvrtcGetPTX.restype = c_int

        self._lib.nvrtcGetProgramLogSize.argtypes = [
            c_void_p,           # prog
            POINTER(c_size_t)   # logSizeRet
        ]
        self._lib.nvrtcGetProgramLogSize.restype = c_int

        self._lib.nvrtcGetProgramLog.argtypes = [
            c_void_p,           # prog
            c_char_p            # log
        ]
        self._lib.nvrtcGetProgramLog.restype = c_int

        self._lib.nvrtcAddNameExpression.argtypes = [
            c_void_p,           # prog
            c_char_p            # nameExpression
        ]
        self._lib.nvrtcAddNameExpression.restype = c_int

        self._lib.nvrtcGetLoweredName.argtypes = [
            c_void_p,           # prog
            c_char_p,           # nameExpression
            POINTER(c_char_p)   # loweredName
        ]
        self._lib.nvrtcGetLoweredName.restype = c_int

        self._lib.nvrtcGetErrorString.argtypes = [
            c_int               # result
        ]
        self._lib.nvrtcGetErrorString.restype = c_char_p

        self._lib.nvrtcVersion.argtypes = [
            POINTER(c_int),     # major
            POINTER(c_int)      # minor
        ]
        self._lib.nvrtcVersion.restype = c_int

    def _throw_on_error(self, code):
        """
        Raises an NVRTCException is the given code is not NVRTC_SUCCESS.
        """
        if code == NVRTC_SUCCESS:
            return
        else:
            raise NVRTCException(self.nvrtcGetErrorString(code))

    def nvrtcCreateProgram(self, src, name, headers, include_names):
        """
        Creates and returns a new NVRTC program object.
        """
        res = c_void_p()
        headers_array = (c_char_p * len(headers))()
        headers_array[:] = headers
        include_names_array = (c_char_p * len(include_names))()
        include_names_array[:] = include_names
        code = self._lib.nvrtcCreateProgram(byref(res),
                                            c_char_p(src), c_char_p(name),
                                            len(headers),
                                            headers_array, include_names_array)
        self._throw_on_error(code)
        return res

    def nvrtcDestroyProgram(self, prog):
        """
        Destroys the given NVRTC program object.
        """
        code = self._lib.nvrtcDestroyProgram(byref(prog))
        self._throw_on_error(code)
        return

    def nvrtcCompileProgram(self, prog, options):
        """
        Compiles the NVRTC program object into PTX, using the provided options
        array.  See the NVRTC API documentation for accepted options.
        """
        options_array = (c_char_p * len(options))()
        options_array[:] = options
        code = self._lib.nvrtcCompileProgram(prog, len(options), options_array)
        self._throw_on_error(code)
        return

    def nvrtcGetPTX(self, prog):
        """
        Returns the compiled PTX for the NVRTC program object.
        """
        size = c_size_t()
        code = self._lib.nvrtcGetPTXSize(prog, byref(size))
        self._throw_on_error(code)

        buf = create_string_buffer(size.value)
        code = self._lib.nvrtcGetPTX(prog, buf)
        self._throw_on_error(code)

        return buf.value.decode('utf-8')

    def nvrtcGetProgramLog(self, prog):
        """
        Returns the log for the NVRTC program object.

        Only useful after calls to nvrtcCompileProgram or nvrtcVerifyProgram.
        """
        size = c_size_t()
        code = self._lib.nvrtcGetProgramLogSize(prog, byref(size))
        self._throw_on_error(code)

        buf = create_string_buffer(size.value)
        code = self._lib.nvrtcGetProgramLog(prog, buf)
        self._throw_on_error(code)

        return buf.value.decode('utf-8')

    def nvrtcAddNameExpression(self, prog, name_expression):
        """
        Notes the given name expression denoting a __global__ function or
        function template instantiation.
        """
        code = self._lib.nvrtcAddNameExpression(prog,
                                                c_char_p(name_expression))
        self._throw_on_error(code)
        return

    def nvrtcGetLoweredName(self, prog, name_expression):
        """
        Notes the given name expression denoting a __global__ function or
        function template instantiation.
        """
        lowered_name = c_char_p()
        code = self._lib.nvrtcGetLoweredName(prog,
                                             c_char_p(name_expression),
                                             byref(lowered_name))
        self._throw_on_error(code)
        return lowered_name.value.decode('utf-8')

    def nvrtcGetErrorString(self, code):
        """
        Returns a text identifier for the given NVRTC status code.
        """
        code_int = c_int(code)
        res = self._lib.nvrtcGetErrorString(code_int)
        return res.decode('utf-8')

    def nvrtcVersion(self):
        """
        Returns the loaded NVRTC library version as a (major, minor) tuple.
        """
        major = c_int()
        minor = c_int()
        code = self._lib.nvrtcVersion(byref(major), byref(minor))
        self._throw_on_error(code)
        return (major.value, minor.value)

    def __str__(self):
        (major, minor) = self.nvrtcVersion()
        return 'NVRTC Interface (Version: %d.%d)' % (major, minor)

    def __repr__(self):
        return str(self)
