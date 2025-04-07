#!/bin/bash

# Print usage information
print_usage() {
    echo "Usage: ./run.sh <data_file> <number_of_frames> [options]"
    echo ""
    echo "Required arguments:"
    echo "  <data_file>         Name of data file in data/ directory (without .txt extension)"
    echo "  <number_of_frames>  Number of animation frames to generate"
    echo ""
    echo "Options for simulation:"
    echo "  -gpu                Run simulation on GPU instead of CPU"
    echo ""
    echo "Options for visualization:"
    echo "  -vectors            Show velocity vectors in the animation"
    echo "  -vmax=<value>       Maximum value for color scale (default: 0.3)"
    echo "  -colorbar           Display colorbar in the animation"
    echo "  -tight              Use tight layout to minimize margins (default: true)"
    echo "  -no-tight           Disable tight layout"
}

# Check if at least two parameters are provided
if [ "$#" -lt 2 ]; then
    print_usage
    exit 1
fi

# Check if data file exists
DATA_FILE="data/$1.txt"
if [ ! -f "$DATA_FILE" ]; then
    echo "Error: Data file '$DATA_FILE' does not exist."
    exit 1
fi

mkdir -p outputs

# Default values
USE_GPU=false
SHOW_VECTORS=false
VMAX="0.3"
SHOW_COLORBAR=false
USE_TIGHT=true

# Parse optional arguments
for arg in "$@"; do
    if [ "$arg" == "-gpu" ]; then
        USE_GPU=true
    elif [ "$arg" == "-vectors" ]; then
        SHOW_VECTORS=true
    elif [[ "$arg" == -vmax=* ]]; then
        VMAX="${arg#-vmax=}"
    elif [ "$arg" == "-colorbar" ]; then
        SHOW_COLORBAR=true
    elif [ "$arg" == "-tight" ]; then
        USE_TIGHT=true
    elif [ "$arg" == "-no-tight" ]; then
        USE_TIGHT=false
    fi
done

# Run LBM simulation
if [ "$USE_GPU" = true ]; then
    ./build/lbm "$DATA_FILE" $2 -gpu
else
    ./build/lbm "$DATA_FILE" $2
fi

# Run visualization
source env/bin/activate

# Build the plotting command with optional arguments
PLOT_CMD="python scripts/plotting2D.py outputs/velocity_out.txt"
if [ "$SHOW_VECTORS" = true ]; then
    PLOT_CMD="$PLOT_CMD -vectors"
fi
PLOT_CMD="$PLOT_CMD -vmax=$VMAX"
if [ "$SHOW_COLORBAR" = true ]; then
    PLOT_CMD="$PLOT_CMD -colorbar"
fi
if [ "$USE_TIGHT" = true ]; then
    PLOT_CMD="$PLOT_CMD -tight"
fi

# Execute the plotting command
eval $PLOT_CMD

if [ "$1" != "lid-driven-cavity" ]; then
    python scripts/dragLift.py outputs/lift_drag_out.txt
fi