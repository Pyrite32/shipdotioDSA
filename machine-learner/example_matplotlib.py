import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.plot(x,y)
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Example Thing")
plt.show()