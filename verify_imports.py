try:
    import streamlit
    import plotly
    import pandas
    import numpy
    print("Imports Successful: streamlit, plotly, pandas, numpy")
except ImportError as e:
    print(f"Import Failed: {e}")
    exit(1)
