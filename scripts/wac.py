# PlanetX Lite - глобус PlanetX без QGIS.
# Copyright (C) 2026 ООО «Информ++». Лицензия Apache 2.0.
# SPDX-License-Identifier: Apache-2.0
"""Тайлы снимков тела из глобальной мозаики COG.

python3 wac.py адрес центральный_меридиан папка уровень_от уровень_до

Мозаика - глобальный растр в простой цилиндрической проекции тела,
охват 360° по долготе и 180° по широте, один канал 8 бит (LROC WAC
USGS). Файл читается по сети через /vsicurl/, GDAL сам берёт уровень
обзора под прореживание. Центральный меридиан проекции - аргумент:
у WAC 180°, край файла - нулевой меридиан. Тайлы 256 × 256 в Web
Mercator тела, разметка XYZ, папка/{z}/{x}/{y}.png, серый PNG.
"""
import math
import os
import sys

import numpy as np
from osgeo import gdal
from PIL import Image

gdal.UseExceptions()
SIZE = 256


def tile_lats(z, y):
    t = (y + (np.arange(SIZE) + 0.5) / SIZE) / 2 ** z
    return np.degrees(np.arctan(np.sinh(math.pi * (1.0 - 2.0 * t))))


def tile_lons(z, x):
    return (x + (np.arange(SIZE) + 0.5) / SIZE) / 2 ** z * 360.0 - 180.0


def build(url, clon, out, z_from, z_to):
    ds = gdal.Open("/vsicurl/" + url)
    band = ds.GetRasterBand(1)
    w, h = ds.RasterXSize, ds.RasterYSize
    gt = ds.GetGeoTransform()
    per_lon = w * gt[1] / 360.0
    per_lat = h * -gt[5] / 180.0
    lon0 = clon + gt[0] / per_lon
    lat0 = gt[3] / per_lat
    deg_x, deg_y = 360.0 / w, 180.0 / h
    print("grid %d x %d, lon0 %.5f, lat0 %.5f" % (w, h, lon0, lat0), flush=True)
    for z in range(z_from, z_to + 1):
        n = 2 ** z
        # Пиксель прочитанной полосы - не крупнее половины пикселя тайла.
        step = max(1, int(w / (SIZE * n * 2)))
        for y in range(n):
            lats = tile_lats(z, y)
            r0 = max(0, int(math.floor((lat0 - lats[0]) / deg_y)) - 2)
            r1 = min(h, int(math.ceil((lat0 - lats[-1]) / deg_y)) + 2)
            rows = r1 - r0
            bw, bh = max(1, w // step), max(1, rows // step)
            a = band.ReadAsArray(0, r0, w, rows, buf_xsize=bw, buf_ysize=bh,
                                 resample_alg=gdal.GRIORA_Average).astype(np.float32)
            dy, dx = rows * deg_y / bh, 360.0 / bw
            top = lat0 - r0 * deg_y
            fy = (top - lats) / dy - 0.5
            y0 = np.clip(np.floor(fy).astype(int), 0, bh - 1)
            y1 = np.clip(y0 + 1, 0, bh - 1)
            ty = np.clip(fy - np.floor(fy), 0.0, 1.0)[:, None]
            for x in range(n):
                fx = ((tile_lons(z, x) - lon0) % 360.0) / dx - 0.5
                x0 = np.floor(fx).astype(int) % bw
                x1 = (x0 + 1) % bw
                tx = fx - np.floor(fx)
                v = (a[y0][:, x0] * (1 - tx) + a[y0][:, x1] * tx) * (1 - ty) \
                    + (a[y1][:, x0] * (1 - tx) + a[y1][:, x1] * tx) * ty
                folder = os.path.join(out, str(z), str(x))
                os.makedirs(folder, exist_ok=True)
                Image.fromarray(np.clip(np.rint(v), 0, 255).astype(np.uint8), "L").save(
                    os.path.join(folder, "%d.png" % y), optimize=True)
        print("level %d: %d tiles" % (z, n * n), flush=True)


if __name__ == "__main__":
    build(sys.argv[1], float(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
