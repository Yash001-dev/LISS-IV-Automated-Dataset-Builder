import rasterio

DEM_1 = rasterio.open(
    "dem/SRTMGL1_1.tif"
)

DEM_2 = rasterio.open(
    "dem/SRTMGL1_2.tif"
)


def get_elevation(
    lat,
    lon
):

    try:

        row, col = DEM_1.index(
            lon,
            lat
        )

        elevation = DEM_1.read(
            1
        )[row, col]

        return float(
            elevation
        )

    except:

        pass

    try:

        row, col = DEM_2.index(
            lon,
            lat
        )

        elevation = DEM_2.read(
            1
        )[row, col]

        return float(
            elevation
        )

    except:

        pass

    return -9999