import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import simpledialog

# Constants
rod_length = 2  # length of the rod in meters
pivot = (0, 0)  # position of the pivot (fixed end)
angular_velocity = 0  # initial angular velocity

# Initialize global variables
masses = [(2, 1), (3, 1.5)]  # default mass list (mass, position from pivot)
torque = 1  # driving torque (Nm)


# Function to calculate moment of inertia
def calculate_moment_of_inertia(masses):
    I = 0
    for mass, position in masses:
        I += mass * position**2
    return I


# Rotation function
def rotate(x, y, theta):
    x_rot = x * np.cos(theta) - y * np.sin(theta)
    y_rot = x * np.sin(theta) + y * np.cos(theta)
    return x_rot, y_rot


# Function to update the plot
def update_plot(frame, line, masses_plot, angular_velocity):
    global torque
    moment_of_inertia = calculate_moment_of_inertia(masses)
    angular_acceleration = torque / moment_of_inertia
    angular_velocity += angular_acceleration * 0.1  # Update angular velocity over time
    theta = angular_velocity * frame * 0.1  # angle = omega * time

    # Calculate rod end points
    x_rod = np.array([pivot[0], rod_length])
    y_rod = np.array([pivot[1], 0])
    x_rod_rot, y_rod_rot = rotate(x_rod, y_rod, theta)

    line.set_data(x_rod_rot, y_rod_rot)

    # Update mass positions
    x_masses = np.array([m[1] for m in masses])
    y_masses = np.zeros_like(x_masses)
    x_masses_rot, y_masses_rot = rotate(x_masses, y_masses, theta)

    masses_plot.set_data(x_masses_rot, y_masses_rot)
    return line, masses_plot


# GUI for user input
class InertiaSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Moment of Inertia Simulator")

        # Set up the matplotlib figure
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(-rod_length - 1, rod_length + 1)
        self.ax.set_ylim(-rod_length - 1, rod_length + 1)
        self.ax.set_aspect('equal')

        self.rod_line, = self.ax.plot([], [], lw=5, color='blue')
        self.mass_points, = self.ax.plot([], [], 'ro', markersize=10)

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        # Moment of Inertia label
        self.inertia_label = tk.Label(root, text="Moment of Inertia: Calculating...")
        self.inertia_label.pack()

        # Controls
        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack()

        self.add_mass_button = tk.Button(self.controls_frame, text="Add Mass", command=self.add_mass)
        self.add_mass_button.grid(row=0, column=0)

        self.remove_mass_button = tk.Button(self.controls_frame, text="Remove Mass", command=self.remove_mass)
        self.remove_mass_button.grid(row=0, column=1)

        self.torque_label = tk.Label(self.controls_frame, text="Driving Torque (Nm):")
        self.torque_label.grid(row=1, column=0)

        self.torque_scale = tk.Scale(self.controls_frame, from_=0, to=10, orient=tk.HORIZONTAL, command=self.update_torque)
        self.torque_scale.set(torque)
        self.torque_scale.grid(row=1, column=1)

        self.start_button = tk.Button(self.controls_frame, text="Start Simulation", command=self.start_simulation)
        self.start_button.grid(row=2, column=0)

    def add_mass(self):
        # Dialog to input mass and position
        mass = float(simpledialog.askstring("Input", "Enter mass (kg):", parent=self.root))
        position = float(simpledialog.askstring("Input", "Enter position from pivot (m):", parent=self.root))

        masses.append((mass, position))

        # Update moment of inertia label
        I = calculate_moment_of_inertia(masses)
        self.inertia_label.config(text=f"Moment of Inertia: {I:.2f} kg·m²")

    def remove_mass(self):
        if masses:
            masses.pop()

        # Update moment of inertia label
        I = calculate_moment_of_inertia(masses)
        self.inertia_label.config(text=f"Moment of Inertia: {I:.2f} kg·m²")

    def update_torque(self, val):
        global torque
        torque = float(val)

    def start_simulation(self):
        self.animate()

    def animate(self):
        from matplotlib.animation import FuncAnimation
        global angular_velocity
        angular_velocity = 0  # Reset angular velocity when simulation starts
        self.ani = FuncAnimation(self.fig, update_plot, fargs=(self.rod_line, self.mass_points, angular_velocity), frames=np.arange(0, 200, 1), interval=50, blit=True)
        self.canvas.draw()


# Main application
root = tk.Tk()
app = InertiaSimulator(root)
root.mainloop()
