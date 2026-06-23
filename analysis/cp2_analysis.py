import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../data/imu_calibration.csv")

print(df.describe())

plt.figure()
plt.plot(df["time_ms"], df["angle_deg"])
plt.xlabel("Time (ms)")
plt.ylabel("Angle (degrees)")
plt.title("MPU6050 Angle Reading")
plt.grid(True)
plt.savefig("../media/plots/mpu6050_angle_plot.png", dpi=300)
plt.show()