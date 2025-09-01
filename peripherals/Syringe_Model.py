import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

actual_values = np.array([
    np.mean([1.23, 1.235, 1.228, 1.233, 1.23]),
    np.mean([2.483, 2.48, 2.486, 2.475, 2.479]),
    np.mean([2.952, 2.955, 2.948, 2.946, 2.948]),
    np.mean([5.916, 5.902, 5.905, 5.924, 5.918])
])
set_values = np.array([1.2475, 2.495, 2.994, 5.988])

X = actual_values.reshape(-1, 1)
y = set_values

model = LinearRegression()
model.fit(X, y)

print(f"Regression coefficient: {model.coef_[0]:.4f}")
print(f"Intercept: {model.intercept_:.4f}")

desired_output = 1.2475
required_input = model.predict([[desired_output]])
print(f"To achieve an actual output of {desired_output} ML, the input should be adjusted to {required_input[0]:.4f} ML")

# Plot the results
plt.scatter(actual_values, set_values, color='blue', label='Set values')
plt.plot(actual_values, model.predict(X), color='red', linewidth=2, label='Fit line')
plt.xlabel('Actual Measured Value (ML)')
plt.ylabel('Set Value (ML)')
plt.title('Calibration Model for Liquid Dispenser')
plt.legend()
plt.show()