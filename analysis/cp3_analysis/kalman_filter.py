"""
CP3 Kalman filter demo - A1302 raw sensor

Takes a batch of raw (unaveraged) single-sample readings logged while the
pendulum was held still at one angle, and runs them through a basic 1D
Kalman filter to show how much it knocks down sample-to-sample jitter.

This is a "constant value" Kalman filter - it assumes the true signal
isn't changing (since the sensor was held still), so the only thing
fighting it is measurement noise. Q is the process noise (how much we
expect the true value to wander on its own) and R is the measurement
noise (how much we trust each individual reading). Lower R = trust the
sensor more, lower Q = trust the model more.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Raw, single-sample LM358 output voltages logged while holding the
# pendulum at a fixed angle (~90 deg). This is what the sensor looks
# like before any averaging - real jitter, not synthetic noise.
raw_samples = [
    2.963, 2.925, 2.900, 2.897, 2.948, 2.954, 2.913, 2.968, 2.940, 2.933,
    2.986, 2.937, 2.939, 2.933, 2.980, 2.994, 3.008, 2.943, 2.989, 2.935,
    2.969, 2.968, 2.879, 3.014, 3.000, 2.900, 2.963, 2.921, 2.945, 2.978,
    3.012, 2.958, 2.931, 2.967, 2.999, 2.954, 2.918, 2.972, 3.001, 2.944,
    2.926, 2.987, 3.005, 2.962, 2.939, 2.981, 2.953, 2.998, 2.967, 2.930,
    2.971, 2.994, 2.948, 2.964, 3.009, 2.937, 2.978, 2.952, 2.991, 2.943,
    2.965, 3.003, 2.929, 2.972, 2.957, 2.985, 2.946, 2.999, 2.934, 2.968,
    2.955, 2.991, 2.940, 2.977, 3.002, 2.949, 2.963, 2.986, 2.928, 2.971,
    2.954, 2.997, 2.942, 2.968, 2.984, 2.951, 2.973, 2.961, 2.989, 2.945,
]
raw = np.array(raw_samples)


def kalman_filter(z, Q=0.0005, R=0.02):
    """Basic scalar Kalman filter for a value we expect to stay constant."""
    n = len(z)
    xhat = np.zeros(n)
    P = np.zeros(n)

    # Seed the filter with the first measurement
    xhat[0] = z[0]
    P[0] = 1.0

    for k in range(1, n):
        # Predict don't expect the value to move, so the prediction
        # is just last estimate, with a bit of uncertainty added (Q)
        xhat_minus = xhat[k - 1]
        P_minus = P[k - 1] + Q

        # Update - blend the prediction with the new measurement based
        # on the Kalman gain (how much we trust the new reading)
        K = P_minus / (P_minus + R)
        xhat[k] = xhat_minus + K * (z[k] - xhat_minus)
        P[k] = (1 - K) * P_minus

    return xhat


if __name__ == "__main__":
    filtered = kalman_filter(raw)

    print(f"{'Sample':>6} {'Raw':>8} {'Filtered':>10}")
    for i in range(len(raw)):
        print(f"{i:>6} {raw[i]:>8.3f} {filtered[i]:>10.3f}")

    print(f"\nRaw std dev:      {raw.std():.4f} V")
    print(f"Filtered std dev: {filtered.std():.4f} V")
    print(f"Noise reduction:  {(1 - filtered.std()/raw.std()) * 100:.1f}%")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(raw, label="Raw (unfiltered)", color="tab:red", alpha=0.6, linewidth=1)
    ax.plot(filtered, label="Kalman filtered", color="tab:blue", linewidth=2)
    ax.set_xlabel("Sample number")
    ax.set_ylabel("LM358 output voltage (V)")
    ax.set_title("CP3 - Kalman Filter: Raw vs Filtered Sensor Output (held position)")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("kalman_plot.png", dpi=150)
    print("\nSaved kalman_plot.png")