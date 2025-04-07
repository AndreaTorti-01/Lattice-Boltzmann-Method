import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import sys
import time
import argparse


def load_velocity_data(filename):
    """
    Load velocity data from a file.
    
    Args:
        filename: Path to the input file
        
    Returns:
        tuple: (velocity_magnitudes, x_velocities, y_velocities, steps, width, height)
    """
    velocity_magnitudes = []
    x_velocities = []
    y_velocities = []
    steps = []
    
    with open(filename, 'r') as f:
        # Read lattice dimensions
        line = f.readline()
        width, height = [int(x) for x in line.split()]
        length = width * height
        
        frame = 0
        line = f.readline()
        while line:
            step = line.strip()
            
            # Read x-velocities
            line = f.readline()
            ux = [float(x) for x in line.split()]
            
            # Read y-velocities
            line = f.readline()
            uy = [float(x) for x in line.split()]
            
            # Compute velocity magnitudes
            u_magnitude = [np.sqrt(ux[i]**2 + uy[i]**2) for i in range(length)]
            
            velocity_magnitudes.append(u_magnitude)
            x_velocities.append(ux)
            y_velocities.append(uy)
            steps.append(step)
            
            print(f'Loaded frame {frame}')
            frame += 1
            line = f.readline()
    
    # Reshape the 1D lists into 2D arrays
    velocity_magnitudes = np.array(velocity_magnitudes).reshape(-1, height, width)
    x_velocities = np.array(x_velocities).reshape(-1, height, width)
    y_velocities = np.array(y_velocities).reshape(-1, height, width)
    
    return velocity_magnitudes, x_velocities, y_velocities, steps, width, height


def create_update_function(velocity_magnitudes, x_velocities, y_velocities, steps, show_vectors=False, custom_vmax=0.3, show_colorbar=False):
    """
    Create a function to update the plot for each animation frame.
    
    Args:
        velocity_magnitudes: 3D array of velocity magnitudes
        x_velocities: 3D array of x-velocities
        y_velocities: 3D array of y-velocities
        steps: List of step labels
        show_vectors: Whether to show velocity vectors
        custom_vmax: Custom maximum value for color scaling
        show_colorbar: Whether to show the colorbar
        
    Returns:
        function: The update function for animation
    """
    # Get figure dimensions once
    height, width = velocity_magnitudes.shape[1], velocity_magnitudes.shape[2]
    
    def update(frame):
        plt.clf()
        
        # Calculate curl (vorticity)
        dfydx = x_velocities[frame, 2:, 1:-1] - x_velocities[frame, :-2, 1:-1]
        dfxdy = y_velocities[frame, 1:-1, 2:] - y_velocities[frame, 1:-1, :-2]
        curl = dfydx - dfxdy
        
        # Use custom vmax if specified, otherwise calculate from data
        vmax = custom_vmax if custom_vmax > 0 else np.max(velocity_magnitudes)
        ax = plt.gca()
        im = ax.imshow(velocity_magnitudes[frame], origin='upper', cmap='RdBu_r', 
                     vmin=0, vmax=vmax, interpolation='none')
        
        # Set fixed axis limits to prevent vibration
        ax.set_xlim(-0.5, width-0.5)
        ax.set_ylim(height-0.5, -0.5)
        
        if show_colorbar:
            plt.colorbar(im)
            
        plt.title(f'Step {steps[frame]}')
        
        if show_vectors:
            # Calculate the step size for x and y directions - more sample points
            step_x = x_velocities.shape[2] // 15
            step_y = x_velocities.shape[1] // 15
            
            # Create the meshgrid
            X, Y = np.meshgrid(np.arange(step_x//2, x_velocities.shape[2], step_x), 
                              np.arange(step_y//2, x_velocities.shape[1], step_y))
            
            # Plot the quiver plot with black arrows, twice as long (scale = 1.5 instead of 3.0)
            ax.quiver(X, Y, x_velocities[frame, Y, X], y_velocities[frame, Y, X], 
                      color='black', angles='xy', scale=1.5, 
                      width=0.003, headwidth=4, headlength=5)
    
    return update


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Create animation of LBM simulation')
    parser.add_argument('input_file', help='Path to the input file')
    parser.add_argument('-vectors', action='store_true', help='Display velocity vectors')
    parser.add_argument('-vmax', type=float, default=0.3, help='Maximum value for color scale')
    parser.add_argument('-colorbar', action='store_true', help='Display colorbar')
    parser.add_argument('-tight', action='store_true', help='Use tight layout to minimize margins', default=True)
    args = parser.parse_args()
    
    # Load data
    velocity_magnitudes, x_velocities, y_velocities, steps, width, height = load_velocity_data(args.input_file)
    
    # Set up figure with optimized size and resolution
    aspect_ratio = height / width
    fig_width = 8
    fig_height = fig_width * aspect_ratio
    fig = plt.figure(figsize=(fig_width, fig_height), dpi=100)
    
    # Create fixed axes with specific positions to prevent vibration
    ax = plt.axes([0.02, 0.02, 0.96, 0.93])
    
    # Create animation with command line options
    update_func = create_update_function(
        velocity_magnitudes, 
        x_velocities, 
        y_velocities, 
        steps, 
        show_vectors=args.vectors,
        custom_vmax=args.vmax,
        show_colorbar=args.colorbar
    )
    
    # Update function for animation with consistent margins
    def fixed_update(frame):
        update_func(frame)
        # Don't use tight_layout as it may cause inconsistent sizing
    
    animation = FuncAnimation(fig, fixed_update, frames=len(velocity_magnitudes), interval=100, repeat=False)
    
    # Save animation as gif with timestamp
    timestr = time.strftime("%Y%m%d-%H%M%S")
    output_path = f'outputs/movie-{timestr}.gif'
    print(f"Saving animation to {output_path}...")
    print(f"Settings: vectors={args.vectors}, vmax={args.vmax}, colorbar={args.colorbar}, tight={args.tight}")
    animation.save(output_path, fps=10, writer='imagemagick')
    print(f"Animation saved to {output_path}")
    
    # Uncomment to display animation in window
    # plt.show()


if __name__ == "__main__":
    main()