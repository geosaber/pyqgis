# ***QGIS Processing Toolbox Algorithm for Trend Surface Generation***

Tutorial (en): https://github.com/geosaber/pyqgis/wiki

## **Script Python para gerar Superfície de Tendência**

Script para gerar superfície de tendência a partir de pontos

## **Como Instalar o Script:**

1. **Salve o código** em um arquivo chamado `TrendSurfaceAlgorithm.py`

2. **No QGIS:**
   - Vá para `Processamento → Caixa de Ferramentas`
   - Clique no botão `Scripts` (ícone de pasta)
   - Vá para `Tools → Add Script from File`
   - Selecione o arquivo salvo

3. **Ou coloque na pasta de scripts:**
   - Pasta padrão: `C:\Users\[Usuário]\AppData\Roaming\QGIS\QGIS3\profiles\default\processing\scripts\` (Windows)
   - Ou `~/.local/share/QGIS/QGIS3/profiles/default/processing/scripts/` (Linux)

## **Como Usar:**

1. **Execute o script** através do Processing Toolbox
2. **Parâmetros de entrada:**
   - Camada de pontos
   - Campo com valores Z
   - Grau do polinômio (1=linear, 2=quadrático, etc.)
   - Tamanho da célula
   - Extensão (opcional)
   - Arquivo de saída

## **Funcionalidades:**

- ✅ Suporte a diferentes graus polinomiais
- ✅ Ajuste por mínimos quadrados
- ✅ Configuração de resolução espacial
- ✅ Define SRC automaticamente
- ✅ Feedback de progresso
- ✅ Tratamento de erros

O script criará um raster contendo a superfície de tendência baseada nos seus pontos de entrada!

---

## **Python Script to Generate a Trend Surface**

Script to generate a trend surface from points

## **How to Install the Script:**
1. ***Save the code*** in a file called `TrendSurfaceAlgorithm.py`

2. **In QGIS:**
   - Go to Processing → Toolbox
   - Click the Scripts button (folder icon)
   - Go to Tools → Add Script from File
   - Select the saved file

3. **Or place it in the scripts folder:**
   - Default folder: `C:\Users\[User]\AppData\Roaming\QGIS\QGIS3\profiles\default\processing\scripts\` (Windows)
   - Or `~/.local/share/QGIS/QGIS3/profiles/default/processing/scripts/` (Linux)

## **How to Use:**
1. **Run the script** through the Processing Toolbox
2. **Input Parameters:**
   - Point Layer
   - Z-Value Field
   - Degree polynomial (1=linear, 2=quadratic, etc.)
   - Cell size
   - Extent (optional)
   - Output file

## **Features:**

- ✅ Support for different polynomial degrees
- ✅ Least squares fitting
- ✅ Spatial resolution setting
- ✅ Automatically sets CRS
- ✅ Progress feedback
- ✅ Error handling

The script will create a raster containing the trend surface based on your input points!

---

# ***QGIS Algorithm Smooth Contours from Raster***

## Instalação:

1. **Salve o código** em um arquivo chamado `smooth_contours.py`

2. **No QGIS**:
   - Vá para `Processamento > Caixa de Ferramentas`
   - Clique no botão `Scripts` (ícone de pasta com +)
   - Selecione `Adicionar Script do Arquivo`
   - Navegue até o arquivo `smooth_contours.py`

## Uso:

1. **Abra a Caixa de Ferramentas de Processamento** (`Processamento > Caixa de Ferramentas`)

2. **Encontre o algoritmo** em `Scripts > Custom > Contornos Suaves a partir de Raster`

3. **Parâmetros disponíveis**:
   - **Raster de entrada**: Seu raster de elevação
   - **Intervalo entre curvas**: Espaçamento entre as curvas de nível
   - **Método de suavização**: 
     - Gaussian: Suavização mais natural
     - Median: Preserva bordas melhor
     - Mean: Suavização uniforme
   - **Grau de suavização**: Número de iterações (1-10)
   - **Tolerância de simplificação**: Simplifica a geometria final

## Vantagens sobre as ferramentas nativas:

- ✅ **Contornos suaves** sem serrilhados
- ✅ **Múltiplos métodos** de suavização
- ✅ **Controle fino** sobre o nível de suavização
- ✅ **Preserva metadados** das curvas de nível
- ✅ **Integração completa** com o Processing Toolbox

O algoritmo combina suavização do raster original com suavização vetorial pós-processamento para obter resultados muito mais suaves que as ferramentas padrão do QGIS.

## Principais correções feitas:

1. **Corrigido o erro do `noDataValue`**:
   - Substituído `band_stats.noDataValue` por `raster_layer.dataProvider().sourceNoDataValue(1)`

2. **Melhor tratamento de erros**:
   - Verificação se a camada de contornos é válida
   - Verificação se foram geradas feições
   - Melhor feedback para o usuário

3. **Progresso corrigido**:
   - Cálculo correto da porcentagem de progresso

4. **Limpeza de arquivos temporários**:
   - Verificação se os arquivos existem antes de tentar remover

5. **Adicionada documentação**:
   - `shortHelpString()` com explicações detalhadas

## Como usar a versão corrigida:

1. **Salve o código corrigido** em um arquivo `.py`
2. **Adicione ao Processing Toolbox** como antes
3. **Execute o algoritmo** - agora deve funcionar sem erros

O algoritmo agora irá:
- ✅ Gerar contornos suaves sem serrilhados
- ✅ Lidar corretamente com valores NoData
- ✅ Fornecer feedback informativo durante o processamento
- ✅ Limpar arquivos temporários automaticamente

# Estilo para Camada de Contornos (QML)

Aqui está um estilo completo para QGIS que diferencia linhas mestras (index contours) das linhas normais, incluindo simbologia e rótulos:

## 1. Como Aplicar o Estilo:

### Método 1: Salvar como Arquivo QML
1. **Salve o código acima** em um arquivo chamado `contornos_suaves.qml`
2. **No QGIS**: Clique direito na camada > `Propriedades` > `Estilo` > `Carregar Estilo`
3. **Selecione o arquivo** `.qml` salvo

### Método 2: Configurar Manualmente

#### Simbologia:
1. **Vá para** `Propriedades da Camada` > `Simbologia`
2. **Selecione** `Renderizador baseado em regras`
3. **Adicione as regras**:

**Regra 1 - Linhas Mestras (100 em 100):**
```
Filtro: "elevation" % 100 = 0
- Cor: Preto (#000000)
- Espessura: 0.66 mm
- Estilo: Linha sólida

```

**Regra 2 - Linhas Intermediárias (50 em 50):**
```
Filtro: "elevation" % 50 = 0 AND "elevation" % 100 != 0
- Cor: Preto (#000000)  
- Espessura: 0.46 mm
- Estilo: Linha sólida
```

**Regra 3 - Linhas Normais:**
```
Filtro: ELSE
- Cor: Cinza escuro (#646464)
- Espessura: 0.26 mm
- Estilo: Linha sólida
```

#### Rótulos:
1. **Vá para** `Propriedades da Camada` > `Rótulos`
2. **Selecione** `Rotulação baseada em regras`
3. **Configure as regras**:

**Regra 1 - Rótulos Linhas Mestras:**
```
Filtro: "elevation" % 100 = 0
Expressão: format_number("elevation",0) || ' m'
Fonte: Arial, Negrito, 10pt
Buffer: Branco, 1.5mm
Posicionamento: Ao longo da linha
```

**Regra 2 - Rótulos Linhas Intermediárias (Opcional):**
```
Filtro: "elevation" % 50 = 0 AND "elevation" % 100 != 0
Expressão: format_number("elevation",0)
Fonte: Arial, Normal, 8pt
Buffer: Branco, 1.0mm
```

## 2. Características do Estilo:

- **Linhas Mestras**: Mais espessas (0.66mm), pretas, com rótulos em negrito
- **Linhas Intermediárias**: Espessura média (0.46mm), pretas, rótulos opcionais
- **Linhas Normais**: Mais finas (0.26mm), cinza, sem rótulos
- **Rótulos**: Com buffer branco para melhor legibilidade
- **Hierarquia visual** clara para fácil interpretação do relevo

## 3. Personalização:

Você pode ajustar facilmente:
- **Intervalos**: Modifique os filtros (100, 50) conforme seu intervalo de contorno
- **Cores**: Altere as cores RGB nos símbolos
- **Espessuras**: Ajuste as espessuras das linhas
- **Fontes**: Modifique família, tamanho e estilo das fontes

Este estilo criará uma visualização profissional e fácil de interpretar para suas curvas de nível!
