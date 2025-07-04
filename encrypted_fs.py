#!/usr/bin/env python
from __future__ import print_function, absolute_import, division
# Import the crypto utilities for encryption
from crypto_utils import *
import logging
from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

if not hasattr(__builtins__, 'bytes'):
    bytes = str


class EncryptedFS(LoggingMixIn, Operations):
    'An encrypted FS that supports only one level of files.'

    def __init__(self):
        self.files = {}
        self.data = defaultdict(bytes)
        self.fd = 0
        now = time()
        self.files['/'] = dict(
            st_mode=(S_IFDIR | 0o755),
            st_ctime=now,
            st_mtime=now,
            st_atime=now,
            st_nlink=2,
            st_size=0)
        # The encryption cypher is initialized
        self.cipher = load_cipher()


    def chmod(self, path, mode):
        self.files[path]['st_mode'] &= 0o770000
        self.files[path]['st_mode'] |= mode
        return 0

    def chown(self, path, uid, gid):
        self.files[path]['st_uid'] = uid
        self.files[path]['st_gid'] = gid

    def create(self, path, mode):
        self.files[path] = dict(
            st_mode=(S_IFREG | mode),
            st_nlink=1,
            st_size=0,
            st_ctime=time(),
            st_mtime=time(),
            st_atime=time())

        # the data for the file is initialized as empty bytes
        self.data[path] = encrypt_data(self.cipher, b'')
        self.fd += 1
        return self.fd

    def getattr(self, path, fh=None):
        if path not in self.files:
            raise FuseOSError(ENOENT)

        return self.files[path]

    def getxattr(self, path, name, position=0):
        attrs = self.files[path].get('attrs', {})

        try:
            return attrs[name]
        except KeyError:
            return ''       # Should return ENOATTR

    def listxattr(self, path):
        attrs = self.files[path].get('attrs', {})
        return attrs.keys()

    def mkdir(self, path, mode):
        self.files[path] = dict(
            st_mode=(S_IFDIR | mode),
            st_nlink=2,
            st_size=0,
            st_ctime=time(),
            st_mtime=time(),
            st_atime=time())

        self.files['/']['st_nlink'] += 1

    def open(self, path, flags):
        if path not in self.files:
            raise FuseOSError(ENOENT)
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        # The data is read in its entirety
        encrypted_full_content = self.data[path]

        try:
            # the data is totally decrypted before slicing
            decrypted_data = decrypt_data(self.cipher, encrypted_full_content)
        except Exception as e:
            logging.error("Falha ao descriptografar %s: %s", path, e)
            raise FuseOSError(ENOENT)

        return decrypted_data[offset:offset + size]

    def readdir(self, path, fh):
        return ['.', '..'] + [x[1:] for x in self.files if x != '/']

    def readlink(self, path):
        return self.data[path]

    def removexattr(self, path, name):
        attrs = self.files[path].get('attrs', {})

        try:
            del attrs[name]
        except KeyError:
            pass        # Should return ENOATTR

    def rename(self, old, new):
        self.data[new] = self.data.pop(old)
        self.files[new] = self.files.pop(old)

    def rmdir(self, path):
        # with multiple level support, need to raise ENOTEMPTY if contains any files
        self.files.pop(path)
        self.files['/']['st_nlink'] -= 1

    def setxattr(self, path, name, value, options, position=0):
        # Ignore options
        attrs = self.files[path].setdefault('attrs', {})
        attrs[name] = value

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
        self.files[target] = dict(
            st_mode=(S_IFLNK | 0o777),
            st_nlink=1,
            st_size=len(source))

        self.data[target] = source

    def truncate(self, path, length, fh=None):
        try:
            plaintext = decrypt_data(self.cipher, self.data[path])
        except Exception:
            plaintext = b''

        new_plaintext = plaintext[:length].ljust(length, b'\x00')

        self.data[path] = encrypt_data(self.cipher, new_plaintext)

        self.files[path]['st_size'] = length
        self.files[path]['st_mtime'] = time()

    def unlink(self, path):
        self.data.pop(path)
        self.files.pop(path)

    def utimens(self, path, times=None):
        now = time()
        atime, mtime = times if times else (now, now)
        self.files[path]['st_atime'] = atime
        self.files[path]['st_mtime'] = mtime

    def write(self, path, data, offset, fh):
        try:
            current_plaintext = decrypt_data(self.cipher, self.data[path])
        except Exception:
            current_plaintext = b''

        if offset > len(current_plaintext):
            current_plaintext += b'\x00' * (offset - len(current_plaintext))

        new_plaintext = current_plaintext[:offset] + data
        if offset + len(data) < len(current_plaintext):
            new_plaintext += current_plaintext[offset + len(data):]
        # The complete content is encrypted before being written
        self.data[path] = encrypt_data(self.cipher, new_plaintext)
        # Update the file metadata
        self.files[path]['st_size'] = len(new_plaintext)
        self.files[path]['st_mtime'] = time()

        return len(data)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('mount')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(EncryptedFS(), args.mount, foreground=True)