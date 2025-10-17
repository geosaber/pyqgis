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

# **Enhanced Polynomial Trend Surface Analysis Script (Experimental)**

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
