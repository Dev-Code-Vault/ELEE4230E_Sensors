import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# calibration Data 
# Actual angles (phone level app reference)
actual_angles = np.array([0, 5, 10, 15, 20, 25], dtype=float)

# MPU6050 averages per angle (raw — axis inverted due to upright board orientation)
# Negating to correct: positive tilt to positive measured angle
mpu_raw_avgs = np.array([0.00, -6.166, -11.015, -15.235, -20.104, -24.558])
mpu = -mpu_raw_avgs  # corrected: [0.00, 6.17, 11.02, 15.24, 20.10, 24.56]

# Linear Regression
n = len(actual_angles)
slope, intercept, r_value, p_value, std_err = stats.linregress(actual_angles, mpu)
R2 = r_value ** 2

print(" TRANSFER FUNCTION")
print(f"  y = {slope:.4f}x + {intercept:.4f}")
print(f"  R² = {R2:.6f}")

# statistics at 20 degrees 
readings_20_raw = np.array([-20.44, -20.23, -20.16, -20.48, -19.55,
                             -20.42, -19.69, -19.69, -20.10, -20.28])
r20 = -readings_20_raw  # corrected

mean_20 = np.mean(r20)
var_20  = np.var(r20, ddof=1)   # sample variance
std_20  = np.std(r20, ddof=1)   # sample std dev

print("\nSTATISTICS AT 20° (n=10)")
print(f"  Mean:     {mean_20:.4f}°")
print(f"  Variance: {var_20:.4f}°²")
print(f"  Std dev:  {std_20:.4f}°")

# Scheffé Confidence Band 
y_pred    = slope * actual_angles + intercept
residuals = mpu - y_pred
MSE       = np.sum(residuals ** 2) / (n - 2)
s         = np.sqrt(MSE)
x_mean    = np.mean(actual_angles)
Sxx       = np.sum((actual_angles - x_mean) ** 2)
F_crit    = stats.f.ppf(0.95, 2, n - 2)        # F(2, n-2, 0.95)

x_fit    = np.linspace(-0.5, 26.5, 400)
y_fit    = slope * x_fit + intercept
h_x      = 1 / n + (x_fit - x_mean) ** 2 / Sxx
scheffe  = np.sqrt(2 * F_crit) * s * np.sqrt(h_x)

print(f"\n SCHEFFE BAND ")
print(f"  MSE = {MSE:.4f},  s = {s:.4f}")
print(f"  F(2, {n-2}, 0.95) = {F_crit:.4f}")
print(f"  Band half-width at x=0:    ±{(np.sqrt(2*F_crit)*s*np.sqrt(1/n+(0-x_mean)**2/Sxx)):.3f}°")
print(f"  Band half-width at x=12.5: ±{(np.sqrt(2*F_crit)*s*np.sqrt(1/n)):.3f}°")
print(f"  Band half-width at x=25:   ±{(np.sqrt(2*F_crit)*s*np.sqrt(1/n+(25-x_mean)**2/Sxx)):.3f}°")

# Plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("CP2 — MPU6050 Transfer Function & Repeatability", fontsize=13)

# Transfer function 
ax1.fill_between(x_fit, y_fit - scheffe, y_fit + scheffe,
                 alpha=0.25, color='darkorange', label="95% Scheffé band")
ax1.plot(x_fit, y_fit, 'r-', lw=1.8,
         label=f"Fit: y = {slope:.4f}x + {intercept:.4f}\n$R^2$ = {R2:.4f}")
ax1.plot(x_fit, x_fit, 'k--', lw=0.9, alpha=0.4, label="Ideal (y = x)")
ax1.scatter(actual_angles, mpu, color='steelblue', zorder=5, s=70, label="Measurements")
ax1.set_xlabel("Actual angle (°)")
ax1.set_ylabel("MPU6050 measured angle (°)")
ax1.set_title("Transfer function with Scheffé band")
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(-1, 27);  ax1.set_ylim(-1, 27)

# repeatability at 20 degrees
ax2.hist(r20, bins=6, color='steelblue', edgecolor='white', alpha=0.8)
ax2.axvline(mean_20, color='red', ls='--', lw=1.8, label=f"Mean = {mean_20:.3f}°")
ax2.axvline(mean_20 - std_20, color='darkorange', ls=':', lw=1.5,
            label=f"±1σ = {std_20:.3f}°")
ax2.axvline(mean_20 + std_20, color='darkorange', ls=':', lw=1.5)
ax2.set_xlabel("Measured angle (°)")
ax2.set_ylabel("Count")
ax2.set_title("Repeatability at 20° (n = 10)")
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("cp2_analysis.png", dpi=150, bbox_inches="tight")
plt.show()
print("\nSaved → cp2_analysis.png")