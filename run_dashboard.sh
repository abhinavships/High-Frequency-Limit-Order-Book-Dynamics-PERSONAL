#!/bin/bash

echo "Starting Limit Order Book Dashboard..."
python -m streamlit run dashboard/app.py
read -p "Press enter to exit..."
