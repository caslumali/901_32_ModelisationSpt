import os
import geopandas as gpd
import rasterio
from rasterio import features  # type: ignore
from rasterio.transform import from_origin
import numpy as np
from scipy import ndimage

# Étape 1 : Charger les couches de lignes et de département
# Remplacez les chemins par ceux de vos fichiers réels
# Votre couche de lignes
lignes = gpd.read_file(
    "C:/Users/robin.heckendorn/Downloads/cycle_toulouse_metropole.geojson")
# Votre couche de département
departement = gpd.read_file("C:/Users/robin.heckendorn/Downloads/tm.shp")

# Vérifier si le système de coordonnées est projeté en mètres
if lignes.crs.is_geographic:
    # Reprojeter en Lambert 93 (EPSG:2154) ou un autre système métrique approprié
    lignes = lignes.to_crs(epsg=2154)

if departement.crs != lignes.crs:
    # Reprojeter le département pour qu'il corresponde au CRS des lignes
    departement = departement.to_crs(lignes.crs)

# Filtrer les géométries invalides ou vides
lignes = lignes[lignes.geometry.notnull() & lignes.geometry.is_valid]
departement = departement[departement.geometry.notnull(
) & departement.geometry.is_valid]

# Réinitialiser les index après le filtrage
lignes = lignes.reset_index(drop=True)
departement = departement.reset_index(drop=True)

# Étape 2 : Obtenir l'emprise (bounding box) du département
minx, miny, maxx, maxy = departement.total_bounds

# Étape 3 : Définir la grille raster avec une résolution de 10 mètres
resolution = 1  # résolution en mètres
largeur = maxx - minx
hauteur = maxy - miny

n_cols = int(np.ceil(largeur / resolution))
n_rows = int(np.ceil(hauteur / resolution))

transform = from_origin(minx, maxy, resolution, resolution)

# Étape 4 : Rasteriser la couche de lignes
raster_shape = (n_rows, n_cols)

# Rasteriser les lignes
shapes_lignes = ((geom, 1) for geom in lignes.geometry)

rasterisé_lignes = features.rasterize(
    shapes=shapes_lignes,
    out_shape=raster_shape,
    transform=transform,
    fill=0,
    all_touched=True,  # Mettre à True pour capturer tous les pixels touchés par les lignes
    dtype=np.uint8
)

# Étape 5 : Calculer la distance à la ligne la plus proche
distance = ndimage.distance_transform_edt(1 - rasterisé_lignes) * resolution

# Convertir en float32 pour réduire la taille tout en conservant la précision
distance = distance.astype('float32')

# Étape 6 : Rasteriser le département pour créer un masque
shapes_departement = ((geom, 1) for geom in departement.geometry)

raster_mask = features.rasterize(
    shapes=shapes_departement,
    out_shape=raster_shape,
    transform=transform,
    fill=0,
    all_touched=True,
    dtype=np.uint8
)

# Appliquer le masque au raster de distance
distance_masked = np.where(raster_mask == 1, distance, np.nan)

# Étape 7 : Enregistrer le raster de distance avec compression LZW
# Changez le chemin si nécessaire
output_directory = 'C:/Users/robin.heckendorn/Downloads/'
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

output_filepath = os.path.join(
    output_directory, 'raster_distance_pistes_cyclables1.tif')

# Définir les options de compression LZW
compress_options = {
    'compress': 'LZW',
    'predictor': 3,
    'tiled': True,
    'blockxsize': 256,
    'blockysize': 256
}

try:
    with rasterio.open(
        output_filepath,
        'w',
        driver='GTiff',
        height=n_rows,
        width=n_cols,
        count=1,
        dtype='float32',
        crs=lignes.crs,
        transform=transform,
        nodata=np.nan,
        **compress_options
    ) as dst:
        dst.write(distance_masked, 1)
    print(f"Le raster est enregistré à l'emplacement : {output_filepath}")
except Exception as e:
    print(f"Erreur lors de l'enregistrement du raster : {e}")
