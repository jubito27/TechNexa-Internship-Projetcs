# Day 7: Dataset Preparation + RandomForest Model + Evaluation
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# -------------------------
# 1. Load Data
# -------------------------
file_path = r"C:\Users\Abhishek sharma\OneDrive\ドキュメント\waste\Final Housing.csv"
data = pd.read_csv(file_path)

print(f"✅ Data loaded successfully! Shape: {data.shape}")

# -------------------------
# 2. Basic Cleaning
# -------------------------
data = data.drop_duplicates()

# Fill missing values (numeric only, example strategy)
numeric_cols = data.select_dtypes(include="number").columns
for col in numeric_cols:
    data[col] = data[col].fillna(data[col].median())

# -------------------------
# 3. Feature/Target Split
# -------------------------
X = data.drop("price", axis=1)
y = data["price"]

# -------------------------
# 4. Train/Test Split
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)
print(f"Train size: {X_train.shape[0]}, Test size: {X_test.shape[0]}")

# -------------------------
# 5. Preprocessing Pipeline
# -------------------------
preprocess_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

X_train_prep = preprocess_pipeline.fit_transform(X_train)
X_test_prep = preprocess_pipeline.transform(X_test)  # transform only!

# -------------------------
# 6. Model Training
# -------------------------
model_rfr = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)
model_rfr.fit(X_train_prep, y_train)

# -------------------------
# 7. Predictions & Evaluation
# -------------------------
y_pred = model_rfr.predict(X_test_prep)

# Calculate metrics
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\n--- Model Evaluation ---")
print(f"RMSE: {rmse:.2f}")
print(f"R²: {r2:.4f}")

# -------------------------
# 8. Optional: Save Model + Pipeline
# -------------------------
import joblib
out_dir = Path("./day07_outputs")
out_dir.mkdir(exist_ok=True)
joblib.dump({"model": model_rfr, "pipeline": preprocess_pipeline}, out_dir / "housing_rfr.joblib")
print(f"\n✅ Model and pipeline saved to {out_dir.resolve()}")
