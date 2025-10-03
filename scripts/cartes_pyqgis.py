import os
from qgis.core import (
    QgsProject,
    QgsLayoutExporter
)

# Caminho da pasta de saída
output_folder = "G:/Meu Drive/Academia/SIGMA/UE/901_32_Modelisation/rapport/cartes/"

# Verificar se a pasta de saída existe e, se não, criar a pasta
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Obter o projeto atual
project = QgsProject.instance()

# Iterar sobre todos os layouts no projeto e exportá-los como PNG
for layout in project.layoutManager().layouts():
    layout_name = layout.name()
    output_path = f"{output_folder}{layout_name}.png"
    exporter = QgsLayoutExporter(layout)
    
    # Configurações de exportação para PNG
    export_settings = QgsLayoutExporter.ImageExportSettings()
    export_settings.dpi = 300  # Defina a resolução desejada (300 DPI para alta qualidade)
    
    # Exportar para PNG
    result = exporter.exportToImage(output_path, export_settings)
    if result == QgsLayoutExporter.Success:
        print(f"Mapa '{layout_name}' exportado com sucesso para {output_path}")
    else:
        print(f"Erro ao exportar o mapa '{layout_name}' para {output_path}")
