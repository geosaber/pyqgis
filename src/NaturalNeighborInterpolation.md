# ***Script de interpolação por Vizinhos Naturais para QGIS Processing Toolbox***

## **Para usar este script:**

1. **Salvar o arquivo:** Salve o código como `natural_neighbor_interpolation.py` na pasta de scripts do Processing:
   - Windows: `C:\Users\[usuário]\AppData\Roaming\QGIS\QGIS3\profiles\default\processing\scripts\`
   - Linux: `~/.local/share/QGIS/QGIS3/profiles/default/processing/scripts/`
   - macOS: `~/Library/Application Support/QGIS/QGIS3/profiles/default/processing/scripts/`

2. **Reiniciar o QGIS:** Reinicie o QGIS para carregar o novo script.

3. **Acessar o script:** Vá para **Processing → Toolbox** e procure por "Interpolação por Vizinhos Naturais" na pasta "Scripts".

## **Versão alternativa usando SAGA GIS (mais precisa para Natural Neighbor):**

Se você tiver o SAGA GIS instalado, pode usar esta versão alternativa do script

## **Características do script:**

- Interface amigável com todos os parâmetros necessários
- Feedback de progresso durante a execução
- Validação de parâmetros
- Documentação integrada
- Compatível com o framework de processamento do QGIS

O script criará um raster interpolado usando o método de vizinhos naturais, que é particularmente útil para dados pontuais irregulares e produz superfícies suaves sem necessidade de ajuste de parâmetros complexos.
