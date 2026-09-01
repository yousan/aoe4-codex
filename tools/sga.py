# -*- coding: utf-8 -*-
"""SGA v10 アーカイブと RGD（ゲームデータ）の読み取り。

フォーマットは AOEMods.Essence（MIT ではないが公開されている実装）の
リーダーを参考に、必要な部分だけ Python に書き起こしたもの。
- SGA: AOEMods.Essence/SGA/Core/ArchiveReader.cs
- RGD: AOEMods.Essence/Chunky/RGD/RGDReader.cs
"""
import struct
import zlib


class Sga:
    def __init__(self, path):
        self.f = open(path, 'rb')
        self._read_header()
        self._read_toc()

    # ---------------- ヘッダ ----------------
    def _u(self, fmt):
        n = struct.calcsize(fmt)
        return struct.unpack(fmt, self.f.read(n))

    def _read_header(self):
        f = self.f
        magic = f.read(8)
        if magic != b'_ARCHIVE':
            raise ValueError('not an SGA archive')
        self.version, self.product = self._u('<HH')
        if self.version != 10:
            raise ValueError(f'unsupported SGA version {self.version}')
        self.nice_name = f.read(128).decode('utf-16-le').rstrip('\0')
        (self.blob_off,) = self._u('<Q')
        (self.blob_len,) = self._u('<I')
        (self.data_off,) = self._u('<Q')
        (self.data_len,) = self._u('<Q')
        self._u('<I')          # unknown
        f.read(256)            # signature
        f.seek(self.blob_off)
        (self.toc_off, self.toc_n, self.folder_off, self.folder_n,
         self.file_off, self.file_n, self.str_off, self.str_len,
         self.hash_off, self.hash_len, self.block_size) = self._u('<11I')

    def _read_toc(self):
        f = self.f
        f.seek(self.blob_off + self.str_off)
        strings = f.read(self.str_len)

        def name_at(off):
            end = strings.index(b'\0', off)
            return strings[off:end].decode('utf-8', 'replace')

        f.seek(self.blob_off + self.toc_off)
        tocs = []
        for _ in range(self.toc_n):
            alias = f.read(64).split(b'\0')[0].decode('utf-8', 'replace')
            name = f.read(64).split(b'\0')[0].decode('utf-8', 'replace')
            tocs.append((alias, name) + self._u('<5I'))

        f.seek(self.blob_off + self.folder_off)
        folders = [self._u('<5I') for _ in range(self.folder_n)]

        f.seek(self.blob_off + self.file_off)
        files = []
        for _ in range(self.file_n):
            name_off, hash_off = self._u('<II')
            (data_off,) = self._u('<Q')
            clen, ulen = self._u('<II')
            verify, storage = self._u('<BB')
            (crc,) = self._u('<I')
            files.append(dict(name_off=name_off, data_off=data_off, clen=clen,
                              ulen=ulen, storage=storage))

        # フォルダを辿ってフルパスを組み立てる
        self.entries = {}
        for toc in tocs:
            root = toc[6]
            stack = [(root, '')]
            while stack:
                idx, prefix = stack.pop()
                fname_off, fs, fe, s, e = folders[idx]
                folder_name = name_at(fname_off)
                for ci in range(fs, fe):
                    stack.append((ci, ''))
                for fi in range(s, e):
                    fl = files[fi]
                    self.entries[f'{folder_name}/{name_at(fl["name_off"])}'.lstrip('/')] = fl

    # ---------------- 読み出し ----------------
    def read(self, path):
        e = self.entries[path]
        self.f.seek(self.data_off + e['data_off'])
        blob = self.f.read(e['clen'])
        if e['clen'] != e['ulen']:
            blob = zlib.decompress(blob)
        return blob

    def names(self):
        return self.entries.keys()


# ---------------- RGD ----------------
FLOAT, INT, BOOL, CSTRING, LIST, LIST2 = 0, 1, 2, 3, 100, 101


class _R:
    def __init__(self, b):
        self.b = b
        self.p = 0

    def u(self, fmt):
        n = struct.calcsize(fmt)
        v = struct.unpack_from(fmt, self.b, self.p)
        self.p += n
        return v

    def cstr(self):
        end = self.b.index(b'\0', self.p)
        s = self.b[self.p:end].decode('utf-8', 'replace')
        self.p = end + 1
        return s


def _read_list(r):
    (n,) = r.u('<i')
    idx = [r.u('<QiI') for _ in range(n)]   # key, type, offset
    base = r.p
    out = []
    for key, typ, off in idx:
        r.p = base + off
        out.append((key, _read_value(r, typ)))
    return out


def _read_value(r, typ):
    if typ == FLOAT:
        return r.u('<f')[0]
    if typ == INT:
        return r.u('<i')[0]
    if typ == BOOL:
        return bool(r.u('<B')[0])
    if typ == CSTRING:
        return r.cstr()
    if typ in (LIST, LIST2):
        return _read_list(r)
    raise ValueError(f'unknown RGD type {typ}')


class _Multi(list):
    """同じキーが複数あったときの入れ物（順番を保つ）"""


def read_rgd(blob):
    """RGD を dict にして返す"""
    r = _R(blob)
    r.p = 16 + 4 + 4                     # chunky header
    chunks = {}
    while r.p < len(blob) - 16:
        start = r.p
        try:
            ctype = bytes(r.u('<4s')[0]).decode('ascii', 'replace')
            cname = bytes(r.u('<4s')[0]).decode('ascii', 'replace')
            _ver, clen = r.u('<ii')
            (plen,) = r.u('<i')
            r.p += plen
        except Exception:
            break
        if ctype not in ('DATA', 'FOLD'):
            r.p = start
            break
        chunks[(ctype, cname)] = (r.p, clen)
        r.p += clen

    if ('DATA', 'KEYS') not in chunks or ('DATA', 'AEGD') not in chunks:
        raise ValueError('KEYS / AEGD chunk not found')

    pos, _ = chunks[('DATA', 'KEYS')]
    r.p = pos
    (n,) = r.u('<i')
    keys = {}
    for _ in range(n):
        (k,) = r.u('<Q')
        (slen,) = r.u('<i')
        keys[k] = r.b[r.p:r.p + slen].decode('utf-8', 'replace')
        r.p += slen

    pos, _ = chunks[('DATA', 'AEGD')]
    r.p = pos
    r.u('<i')                            # unknown
    table = _read_list(r)

    def to_dict(pairs):
        """同じキーが並ぶことがある（生産キューなど）。その場合は順番を保った配列にする"""
        out = {}
        for k, v in pairs:
            name = keys.get(k, str(k))
            val = conv(v)
            if name in out:
                if isinstance(out[name], list) and getattr(out[name], 'multi', False) is False \
                        and not isinstance(out[name], dict):
                    pass
                cur = out[name]
                if isinstance(cur, _Multi):
                    cur.append(val)
                else:
                    m = _Multi([cur, val])
                    out[name] = m
            else:
                out[name] = val
        return out

    def conv(v):
        if isinstance(v, list):
            return to_dict(v)
        return v

    return to_dict(table)
