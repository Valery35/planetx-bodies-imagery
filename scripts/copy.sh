#!/usr/bin/env bash
# PlanetX Lite - глобус PlanetX без QGIS.
# Copyright (C) 2026 ООО «Информ++». Лицензия Apache 2.0.
# SPDX-License-Identifier: Apache-2.0
#
# Копия цветной мозаики Марса Viking MDIM2.1 (NASA, USGS) из тайлов
# OpenPlanetaryMap, уровни $2..$3, в папку $1 как mars/{z}/{x}/{y}.png.
# У OpenPlanetaryMap ряды в разметке TMS, здесь - XYZ, как у прочих
# тайлов PlanetX. Тайлы копируются как есть, PNG без перекодирования.
# Уже скачанный тайл не просится второй раз. Отсутствующий тайл S3
# отвечает 403 или 404, его просто нет.
set -u
out="$1"
from="${2:-0}"
to="${3:-7}"
src="https://s3-eu-west-1.amazonaws.com/whereonmars.cartodb.net/viking_mdim21_global"
agent="PlanetX-bodies copy (+https://github.com/Valery35/planetx-bodies-imagery)"
export out src agent

one() {
  z="$1"; x="$2"; y="$3"
  file="$out/mars/$z/$x/$y.png"
  [ -s "$file" ] && return 0
  mkdir -p "$out/mars/$z/$x"
  tms=$(( (1 << z) - 1 - y ))
  if curl -fsS --retry 3 --retry-delay 5 --max-time 120 -A "$agent" -o "$file.part" "$src/$z/$x/$tms.png"; then
    mv "$file.part" "$file"
  else
    rm -f "$file.part"
  fi
}
export -f one

for z in $(seq "$from" "$to"); do
  n=$(( 1 << z ))
  for x in $(seq 0 $(( n - 1 ))); do
    for y in $(seq 0 $(( n - 1 ))); do
      echo "$z $x $y"
    done
  done | xargs -P 8 -n 3 bash -c 'one "$@"' _
  echo "level $z: $(find "$out/mars/$z" -name '*.png' | wc -l) tiles, $(du -sh "$out/mars/$z" | cut -f1)"
done
exit 0
