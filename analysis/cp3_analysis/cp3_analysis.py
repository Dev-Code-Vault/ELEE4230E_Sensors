"""
CP3 calibration analysis - A1302 raw sensor

Takes the angle-sweep data logged from the ESP32 (LM358 output voltage
at a bunch of known angles), averages each angle's readings, fits both
a full-range sine model (since a single-axis Hall sensor reading a
rotating diametric magnet is sinusoidal by nature) and a linear model
over the steepest/most usable region of that curve.

Run this after pasting your serial log data into the `data` dict below,
or point it at data/a1302_calibration.csv once that's built.
"""

import numpy as np
from scipy.optimize import curve_fit

# Raw LM358 output voltage readings, grouped by the angle we held the
# pendulum at during calibration. Each list is every individual sample
# logged at that angle (not yet averaged).
data = {
    0:   [1.516, 1.530, 1.533, 1.513, 1.507, 1.519, 1.543, 1.533, 1.575,
          1.512, 1.475, 1.482, 1.545, 1.518, 1.497, 1.511, 1.521, 1.504, 1.5],
    30:  [1.687, 1.725, 1.662, 1.692, 1.703, 1.705, 1.700, 1.720, 1.726,
          1.695, 1.684, 1.663, 1.744, 1.635, 1.696, 1.721, 1.660, 1.662,
          1.729, 1.693, 1.693, 1.675, 1.669],
    60:  [2.287, 2.243, 2.255, 2.238, 2.231, 2.243, 2.159, 2.249, 2.153,
          2.209, 2.206, 2.244, 2.268, 2.211, 2.235, 2.258, 2.277, 2.276,
          2.278, 2.214, 2.241, 2.286, 2.268],
    90:  [2.963, 2.925, 2.900, 2.897, 2.948, 2.954, 2.913, 2.968, 2.940,
          2.933, 2.986, 2.937, 2.939, 2.933, 2.980, 2.994, 3.008, 2.943,
          2.989, 2.935, 2.969, 2.968, 2.879, 3.014, 3.000, 2.9],
    120: [3.390, 3.418, 3.403, 3.409, 3.402, 3.405, 3.398, 3.402, 3.416,
          3.406, 3.403, 3.405, 3.404, 3.391, 3.412, 3.403, 3.398, 3.411,
          3.395, 3.411, 3.405, 3.412, 3.414, 3.406],
    160: [3.412, 3.403, 3.411, 3.408, 3.406, 3.410, 3.413, 3.420, 3.408,
          3.416, 3.408, 3.417, 3.415, 3.417, 3.409, 3.422, 3.422, 3.420,
          3.422, 3.413, 3.414, 3.421],
    180: [3.210, 3.187, 3.233, 3.301, 3.283, 3.264, 3.268, 3.281, 3.274,
          3.258, 3.286, 3.211, 3.302, 3.243, 3.290, 3.229, 3.262, 3.241,
          3.297, 3.246, 3.237, 3.289, 3.281, 3.293, 3.243],
    210: [2.530, 2.560, 2.551, 2.601, 2.540, 2.527, 2.535, 2.526, 2.534,
          2.516, 2.503, 2.659, 2.583, 2.538, 2.654, 2.548, 2.596, 2.574,
          2.549, 2.623, 2.581, 2.617, 2.570, 2.607],
    240: [2.075, 2.001, 1.985, 2.001, 2.057, 2.008, 2.027, 2.017, 1.960,
          1.975, 2.056, 2.003, 2.032, 2.003, 1.975, 1.984, 1.971, 2.008],
    266: [1.598, 1.581, 1.550, 1.603, 1.610, 1.575, 1.558, 1.630, 1.569,
          1.548, 1.554, 1.518, 1.595, 1.509, 1.529, 1.561, 1.544, 1.601,
          1.563, 1.574, 1.590, 1.555, 1.574, 1.566],
    300: [1.227, 1.211, 1.204, 1.211, 1.207, 1.203, 1.221, 1.198, 1.198,
          1.202, 1.200, 1.212, 1.182, 1.201, 1.200, 1.211, 1.210, 1.208,
          1.192, 1.196, 1.208, 1.185, 1.200],
    325: [1.289, 1.315, 1.270, 1.267, 1.286, 1.294, 1.272, 1.284, 1.291,
          1.280, 1.297, 1.293, 1.274, 1.276, 1.293, 1.272, 1.296, 1.289,
          1.284, 1.264, 1.311, 1.283],
}


def average_by_angle(raw_data):
    """Collapse each angle's sample list down to mean + std + count."""
    means = {}
    print(f"{'Angle':>6} {'Mean(V)':>10} {'Std(V)':>10} {'N':>4}")
    for angle, vals in sorted(raw_data.items()):
        arr = np.array(vals)
        means[angle] = arr.mean()
        print(f"{angle:>6} {arr.mean():>10.4f} {arr.std():>10.4f} {len(arr):>4}")
    return means


def fit_sine_model(means):
    """
    Fit V = A*sin(theta + phi) + C across the full 0-360 sweep.
    This is the "raw, nonlinear" transfer function - it's sinusoidal
    because the A1302 only sees the component of the magnetic field
    along its one sensing axis as the diametric magnet rotates past it.
    """
    angles = np.array(sorted(means.keys()))
    volts = np.array([means[a] for a in angles])

    def sine_model(theta_deg, A, phi_deg, C):
        theta = np.radians(theta_deg)
        phi = np.radians(phi_deg)
        return A * np.sin(theta + phi) + C

    popt, _ = curve_fit(sine_model, angles, volts, p0=[1.1, 0, 2.2])
    A, phi, C = popt
    pred = sine_model(angles, *popt)
    ss_res = np.sum((volts - pred) ** 2)
    ss_tot = np.sum((volts - np.mean(volts)) ** 2)
    r2 = 1 - ss_res / ss_tot

    print(f"\nSine fit: V = {A:.4f} * sin(theta + {phi:.2f} deg) + {C:.4f}")
    print(f"R^2 = {r2:.4f}")
    print(f"Peak near theta = {90 - phi:.1f} deg, trough near theta = {270 - phi:.1f} deg")
    return A, phi, C, r2


def fit_linear_region(means, angle_list):
    """
    Fit a straight line through just the steepest/most monotonic chunk
    of the sweep - this is the region you'd actually want to operate in
    if you were using this sensor for real angle measurement.
    """
    angles = np.array(angle_list)
    volts = np.array([means[a] for a in angle_list])
    slope, intercept = np.polyfit(angles, volts, 1)
    pred = np.polyval([slope, intercept], angles)
    ss_res = np.sum((volts - pred) ** 2)
    ss_tot = np.sum((volts - np.mean(volts)) ** 2)
    r2 = 1 - ss_res / ss_tot

    print(f"\nLinear fit ({angle_list[0]} to {angle_list[-1]} deg):")
    print(f"V = {slope:.5f} * angle + {intercept:.4f}")
    print(f"R^2 = {r2:.4f}")

    print("\nResiduals (actual - predicted):")
    for a, v, p in zip(angles, volts, pred):
        print(f"  angle={a:>4}  actual={v:.4f}  predicted={p:.4f}  residual={v - p:+.4f}")

    return slope, intercept, r2


if __name__ == "__main__":
    means = average_by_angle(data)
    fit_sine_model(means)
    fit_linear_region(means, [0, 30, 60, 90, 120])