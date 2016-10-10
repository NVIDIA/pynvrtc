==================================
pynvrtc - Python Bindings to NVRTC
================================== 

Introduction
============

The pynvrtc package is a Python binding for NVRTC, the CUDA runtime
compilation library from NVIDIA.  This library takes CUDA source input and
produces NVIDIA PTX output suitable for execution on NVIDIA GPUs on any
platform.  Please see the CUDA 8.0 documentation for a complete description of
NVRTC.


Installation
============

The pynvrtc package does not have any external dependencies and can be
installed with ``pip`` or ``easy_install``.

::

    $ pip install pynvrtc

Note, however, that the package does require the NVRTC library to be present
at runtime. See below for instructions on how to set the search path.


Using pynvrtc
=============

There are two primary interfaces with pynvrtc; a low-level interface which
provides users with direct access to the NVRTC API, and a high-level
interface which provides a Pythonic API for the compiler routines in NVRTC.


Low-Level Interface
-------------------

The low-level interface can be found in the ``pynvrtc.interface`` module. An
instance of the interface can be obtained by calling the ``NVRTCInterface``
constructor:

::

    from pynvrtc.interface import NVRTCInterface

    inter = NVRTCInterface()

By default, the ``NVRTCInterface`` object will attempt to load the NVRTC
shared library from ``LD_LIBRARY_PATH`` on Linux, ``DYLD_LIBRARY_PATH`` on
Mac, or ``PATH`` on Windows.  An optional parameter to the ``NVRTCInterface``
constructor provides the absolute path to the NVRTC shared library and
overwrites the system search path.  For example, on Linux:

::

    from pynvrtc.interface import NVRTCInterface

    inter = NVRTCInterface('/usr/local/cuda-8.0/nvrtc/lib64/libnvrtc.so')

**NOTE**: It is important that the specified binary match the architecture of
the Python interpreter under which your program is running.

Once an interface object is created, it provides access to all of the NVRTC
API functions as regular Python functions. However, instead of returning a
NVRTC status code, each function returns either a string (for output
functions) or None.  If an error occurs within NVRTC, an ``NVRTCException``
exception is raised with the corresponding status code.

Note that the ``nvrtcGetProgramLogSize`` and ``nvrtcGetPTXSize``
functions are *not* exposed.  Instead, the ``nvrtcGetProgramLog`` and
``nvrtcGetPTX`` functions automatically determine the correct size
and return a UTF-8 encoded Python string.

Full Example:

::

    from pynvrtc.interface import NVRTCInterface, NVRTCException

    src = ... ## Populate CUDA source code

    inter = NVRTCInterface()

    try:
        prog = inter.nvrtcCreateProgram(src, 'simple.cu', [], []);
        inter.nvrtcCompileProgram(prog, ['-ftz=true'])
        ptx = inter.nvrtcGetPTX(prog)
    except NVRTCException as e:
        print('Error: %s' % repr(e))



High-Level Interface
--------------------

For clients wanting a higher-level interface to NVRTC, the ``Program`` class
in ``pynvrtc.compiler`` provides such an interface. The usage is similar to
that of the ``NVRTCInterface`` class, but the API is more Pythonic and you do
not need to worry about maintaining NVRTC objects.

::

    from pynvrtc.compiler import Program, ProgramException

    src = ... ## Populate CUDA source code

    try:
        prog = Program(src, 'simple.cu')
        ptx = prog.compile(['-ftz=1'])
    except ProgramException as e:
        print('Error: %s' % repr(e))

As with ``NVRTCInterface``, the ``Program`` constructor accepts an optional
path to the NVRTC library.

Please see ``samples/ptxgen.py`` for a complete example of a CUDA source to
PTX compiler using the higher-level interface.
