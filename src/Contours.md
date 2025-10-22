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
