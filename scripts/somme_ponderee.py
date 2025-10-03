import numpy as np
import rasterio

# Fichiers raster
raster_paths = ["raster_age_brut.tif", "raster_diplome_brut.tif", "raster_revenu_brut.tif"]

# Coefficients de pondération
weights = [0.3, 0.6, 0.1]

# Valeur NoData définie explicitement
nodata_value = -9999

# Ouvrir le premier raster pour récupérer les métadonnées
with rasterio.open(raster_paths[0]) as src:
    meta = src.meta
    meta.update(nodata=nodata_value)  # Mettre à jour les métadonnées avec la valeur NoData

# Créer un tableau pour la somme pondérée
weighted_sum = None

# Parcourir les rasters et appliquer les coefficients
for i, path in enumerate(raster_paths):
    with rasterio.open(path) as src:
        data = src.read(1)

        # Gérer les NoData en les remplaçant par 0 temporairement pour éviter les erreurs de calcul
        data = np.where(data == nodata_value, 0, data)

        # Appliquer le coefficient de pondération
        weighted_raster = data * weights[i]

        # Initialiser la somme pondérée si nécessaire
        if weighted_sum is None:
            weighted_sum = np.zeros_like(weighted_raster)

        # Ajouter le raster pondéré à la somme
        weighted_sum += weighted_raster

# Restaurer les valeurs NoData dans le raster final
weighted_sum = np.where(weighted_sum == 0, nodata_value, weighted_sum)

# Enregistrer le raster final
meta.update(dtype=rasterio.float32)  # Modifier le type de données si nécessaire
with rasterio.open("raster_pondere_final.tif", 'w', **meta) as dst:
    dst.write(weighted_sum.astype(rasterio.float32), 1)

print("Le raster final a été créé avec succès.")
