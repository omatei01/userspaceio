# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
libperipherymmio CFFI interface for MMIO access
-------------

Helper methods added to handle repetitive operations.
"""

from cffi import FFI


class libperipherymmio:

    def __init__(self):
        self.ffi = FFI()
        # Specify each C function, struct and constant you want a Python binding for
        # Copy-n-paste with minor edits
        self.ffi.cdef("""
        typedef unsigned char uint8_t;
        typedef unsigned short int uint16_t;
        typedef unsigned long uint32_t;
        typedef unsigned long uintptr_t;
        typedef unsigned long size_t;
        
        enum mmio_error_code {
            MMIO_ERROR_ARG   = -1,
            MMIO_ERROR_OPEN  = -2,
            MMIO_ERROR_MAP   = -3,
            MMIO_ERROR_CLOSE = -4,
            MMIO_ERROR_UNMAP = -5,
        };
        
        typedef struct mmio_handle {
            uintptr_t base, aligned_base;
            size_t size, aligned_size;
            void *ptr;
        
            struct {
                int c_errno;
                char errmsg[96];
            } error;
        } mmio_t;        
        
        int mmio_open(mmio_t *mmio, uintptr_t base, size_t size);
        
        void *mmio_ptr(mmio_t *mmio);
        
        int mmio_read32(mmio_t *mmio, uintptr_t offset, uint32_t *value);
        
        int mmio_read16(mmio_t *mmio, uintptr_t offset, uint16_t *value);
        
        int mmio_read8(mmio_t *mmio, uintptr_t offset, uint8_t *value);
        
        int mmio_read(mmio_t *mmio, uintptr_t offset, uint8_t *buf, size_t len);
        
        int mmio_write32(mmio_t *mmio, uintptr_t offset, uint32_t value);
        
        int mmio_write16(mmio_t *mmio, uintptr_t offset, uint16_t value);
        
        int mmio_write8(mmio_t *mmio, uintptr_t offset, uint8_t value);
        
        int mmio_write(mmio_t *mmio, uintptr_t offset, const uint8_t *buf, size_t len);
        
        int mmio_close(mmio_t *mmio);
        
        uintptr_t mmio_base(mmio_t *mmio);
        
        size_t mmio_size(mmio_t *mmio);
        
        int mmio_tostring(mmio_t *mmio, char *str, size_t len);

        int mmio_errno(mmio_t *mmio);
        
        const char *mmio_errmsg(mmio_t *mmio);
        """)
        self.lib = self.ffi.dlopen("/usr/local/lib/libperipherymmio.so")
