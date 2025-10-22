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
