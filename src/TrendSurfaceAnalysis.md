# Polynomial Regression with Least Squares

## **1. Understanding Polynomial Regression**

### **What is Polynomial Regression?**
Polynomial regression extends linear regression to model nonlinear relationships by adding polynomial terms:

**Linear Regression:**
```
z = β₀ + β₁x + β₂y
```

**Quadratic Regression:**
```
z = β₀ + β₁x + β₂y + β₃x² + β₄xy + β₅y²
```

**Cubic Regression:**
```
z = β₀ + β₁x + β₂y + β₃x² + β₄xy + β₅y² + β₆x³ + β₇x²y + β₈xy² + β₉y³
```

## **2. Mathematical Foundation**

### **Least Squares Method**
The goal is to minimize the sum of squared residuals:

```
min Σ(z_i - ž_i)²
```

Where:
- `z_i` = observed value at point i
- `ž_i` = predicted value from polynomial

### **Matrix Formulation**
```
A · β = Z
```

Where:
- `A` = Design matrix of polynomial terms
- `β` = Coefficient vector (what we solve for)
- `Z` = Observed values vector

### **Solution using Normal Equations**
```
β = (AᵀA)⁻¹AᵀZ
```

## **3. Step-by-Step Algorithm**

### **Step 1: Data Preparation**
```python
# Input data: x, y coordinates and z values
x = [x₁, x₂, ..., xₙ]
y = [y₁, y₂, ..., yₙ]  
z = [z₁, z₂, ..., zₙ]
```

### **Step 2: Design Matrix Construction**
For degree 2 polynomial:
```python
# Each row: [1, x, y, x², xy, y²]
A = [
    [1, x₁, y₁, x₁², x₁y₁, y₁²],
    [1, x₂, y₂, x₂², x₂y₂, y₂²],
    ...
    [1, xₙ, yₙ, xₙ², xₙyₙ, yₙ²]
]
```

### **Step 3: Solve Least Squares**
```python
# Using numpy's least squares solver
coefficients = np.linalg.lstsq(A, z, rcond=None)[0]
```

### **Step 4: Surface Evaluation**
```python
def evaluate_polynomial(x, y, coeffs, degree):
    value = 0
    idx = 0
    for d in range(degree + 1):
        for j in range(d + 1):
            value += coeffs[idx] * (x ** (d - j)) * (y ** j)
            idx += 1
    return value
```

## **4. Practical Example**

### **Sample Data:**
| Point | X | Y | Z (Elevation) |
|-------|---|---|---------------|
| 1 | 0 | 0 | 100 |
| 2 | 10 | 0 | 110 |
| 3 | 0 | 10 | 105 |
| 4 | 10 | 10 | 115 |

### **Linear Surface (Degree 1):**
```
Design Matrix A:
[[1, 0, 0],
 [1, 10, 0], 
 [1, 0, 10],
 [1, 10, 10]]
 
Solving: A·β = [100, 110, 105, 115]
```

### **Result:**
```
z = 100 + 1.0*x + 0.5*y
```

## **5. Choosing Polynomial Degree**

### **Degree 1 - Linear:**
- Good for simple trends
- 3 coefficients
- Planar surface

### **Degree 2 - Quadratic:**
- Captures curvature
- 6 coefficients
- Can model hills/valleys

### **Degree 3 - Cubic:**
- Complex surfaces
- 10 coefficients
- Risk of overfitting

## **6. Interpretation of Results**

### **Residual Analysis:**
```python
residuals = z_observed - z_predicted
RMSE = np.sqrt(np.mean(residuals**2))
```

### **Goodness of Fit:**
- **R²**: Proportion of variance explained
- **RMSE**: Average prediction error
- **Visual inspection**: Check residual patterns

## **7. Applications in GIS**

### **Topographic Analysis:**
- Regional slope detection
- Geological trend identification
- Climate pattern analysis

### **Environmental Modeling:**
- Pollution gradient mapping
- Temperature surface generation
- Precipitation trend analysis

## **8. Advantages and Limitations**

### **Advantages:**
- Simple mathematical foundation
- Computationally efficient
- Easy to interpret coefficients
- Flexible for different complexities

### **Limitations:**
- Sensitive to outliers
- Assumes global trend (no local variations)
- Can overfit with high degrees
- Extrapolation risks

## **9. Validation Methods**

### **Cross-Validation:**
```python
# Split data into training and testing
train_mask = np.random.choice([True, False], size=len(z), p=[0.7, 0.3])
train_A, test_A = A[train_mask], A[~train_mask]
train_z, test_z = z[train_mask], z[~train_mask]
```

### **Residual Mapping:**
- Create residual raster (observed - predicted)
- Check for spatial patterns
- Identify areas of poor fit

This tutorial provides both the theoretical foundation and practical implementation for polynomial trend surface analysis using least squares regression!
