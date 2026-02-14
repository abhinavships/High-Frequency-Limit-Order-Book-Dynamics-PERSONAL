import sys
import os
import plotly.graph_objects as go

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.visualization.lob_plots import plot_lob_snapshot, plot_spread_evolution, plot_depth_chart
    print("Successfully imported plotting functions.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def validate_plots():
    print("Validating plot_lob_snapshot...")
    fig1 = plot_lob_snapshot()
    if isinstance(fig1, go.Figure):
        print("plot_lob_snapshot returned a plotly Figure.")
    else:
        print("Error: plot_lob_snapshot did not return a Figure.")
        sys.exit(1)

    print("Validating plot_spread_evolution...")
    fig2 = plot_spread_evolution()
    if isinstance(fig2, go.Figure):
        print("plot_spread_evolution returned a plotly Figure.")
    else:
        print("Error: plot_spread_evolution did not return a Figure.")
        sys.exit(1)

    print("Validating plot_depth_chart...")
    fig3 = plot_depth_chart()
    if isinstance(fig3, go.Figure):
        print("plot_depth_chart returned a plotly Figure.")
    else:
        print("Error: plot_depth_chart did not return a Figure.")
        sys.exit(1)

    print("\nAll validations passed!")

if __name__ == "__main__":
    validate_plots()
