# trendsurf
QGIS Processing Toolbox Algorithm for Trend Surface Interpolation

Tutorial (en): https://github.com/geosaber/trendsurf/wiki

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

Enhanced Polynomial Trend Surface Analysis Script (EXPERIMENTAL)
# **Enhanced Polynomial Trend Surface Analysis Script**

## **New Features Added:**

### **1. Advanced Statistical Analysis**
- R², Adjusted R², RMSE, MAE
- AIC and BIC for model selection
- Normality tests for residuals
- Cross-validation with k-fold

### **2. Robust Regression**
- Outlier-resistant fitting
- Iteratively reweighted least squares
- Huber-like weighting function

### **3. Confidence Intervals**
- Prediction uncertainty maps
- Standard errors calculation
- Custom confidence levels

### **4. Comprehensive Outputs**
- Trend surface raster
- Residual raster
- Confidence intervals raster
- Statistical reports
- Residual points layer

### **5. Model Validation**
- Cross-validation metrics
- Model diagnostics
- Overfitting detection

### **6. Weighted Regression**
- Support for weighted least squares
- Variable importance weighting

### **7. Enhanced User Interface**
- More parameters and options
- Better progress feedback
- Optional outputs

This enhanced version provides professional-grade trend surface analysis with comprehensive diagnostics and validation tools!
