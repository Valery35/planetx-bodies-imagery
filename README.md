# planetx-bodies-imagery

Imagery tiles of other bodies for [PlanetX Lite](https://github.com/Valery35/planetx-lite)
and the PlanetX plugin for QGIS.

The OpenPlanetaryMap tiles in Amazon S3 send no CORS header, so a browser
page cannot read them directly. The desktop program can read the source,
and the page reads this copy. The workflow `.github/workflows/copy.yml`
runs `scripts/copy.sh` once by hand and pushes the tiles to `main` in parts.

| Path | Source | Terms |
|---|---|---|
| `mars/{z}/{x}/{y}.png`, levels 0-7 | Mars Viking MDIM2.1 colorized global mosaic, NASA, USGS, via OpenPlanetaryMap tiles | Public domain (NASA, USGS); credit NASA, USGS, Viking MDIM2.1, OpenPlanetaryMap |

The tiles are XYZ Web Mercator of the body sphere, 256 × 256 PNG, copied
without re-encoding. The rows of the OpenPlanetaryMap tiles are TMS,
here they are XYZ.
