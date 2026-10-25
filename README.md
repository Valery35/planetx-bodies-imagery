# planetx-bodies-imagery

Imagery tiles of other bodies for [PlanetX Lite](https://github.com/Valery35/planetx-lite)
and the PlanetX plugin for QGIS.

The OpenPlanetaryMap tiles in Amazon S3 send no CORS header, so a browser
page cannot read them directly. The WAC mosaic has CORS, but a whole-globe
view reads it slowly: PlanetX Lite takes levels 0-7 of the Moon from here
and reads the mosaic itself only closer. The desktop program can read the source,
and the page reads this copy. The workflow `.github/workflows/copy.yml`
runs `scripts/copy.sh` once by hand and pushes the tiles to `main` in parts.

| Path | Source | Terms |
|---|---|---|
| `mars/{z}/{x}/{y}.png`, levels 0-7 | Mars Viking MDIM2.1 colorized global mosaic, NASA, USGS, via OpenPlanetaryMap tiles (`.github/workflows/copy.yml`) | Public domain (NASA, USGS); credit NASA, USGS, Viking MDIM2.1, OpenPlanetaryMap |
| `moon/{z}/{x}/{y}.png`, levels 0-7, grey | Moon LRO LROC WAC global mosaic 100 m, NASA, GSFC, Arizona State University, USGS, cut from the COG in astrogeo-ard (`.github/workflows/wac.yml`) | Public domain; credit NASA, GSFC, Arizona State University, LRO LROC WAC, USGS |

The tiles are XYZ Web Mercator of the body sphere, 256 × 256 PNG, copied
without re-encoding. The rows of the OpenPlanetaryMap tiles are TMS,
here they are XYZ.
