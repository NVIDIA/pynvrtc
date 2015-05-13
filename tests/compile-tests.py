# Copyright (c) 2014-2015, NVIDIA Corporation.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
from util import get_interface

### Low-level interface tests
class CompileTests(unittest.TestCase):
    def test_create_program(self):
        i = get_interface()

        prog = i.nvrtcCreateProgram('__global__ void k() {}\n', 'simple.cu',
                                    [], [])
        i.nvrtcDestroyProgram(prog)

    def test_compile_empty_program(self):
        i = get_interface()

        prog = i.nvrtcCreateProgram('#include "foo.h"\n'
                                    '__global__ void k() {}\n', 'simple.cu',
                                    ['__device__ void f() {}\n'], ['foo.h'])
        i.nvrtcCompileProgram(prog, [])
        i.nvrtcDestroyProgram(prog)

    def test_program_log(self):
        import pynvrtc.interface
        i = get_interface()

        prog = i.nvrtcCreateProgram('__global__ int k() {}\n', 'simple.cu',
                                    [], [])
        self.assertRaises(pynvrtc.interface.NVRTCException,
                          i.nvrtcCompileProgram, prog, [])
        log = i.nvrtcGetProgramLog(prog)
        self.assertTrue(len(log) > 0)
        i.nvrtcDestroyProgram(prog)        

    def test_program_output(self):
        import pynvrtc.interface
        i = get_interface()

        prog = i.nvrtcCreateProgram('__global__ void k() {}\n', 'simple.cu',
                                    [], [])
        i.nvrtcCompileProgram(prog, [])
        ptx = i.nvrtcGetPTX(prog)
        self.assertTrue(len(ptx) > 0)
        i.nvrtcDestroyProgram(prog)  
