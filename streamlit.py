import platform
from glob import glob

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

if platform.system() == "Windows":
    from pathlib import PureWindowsPath as Path
elif platform.system() == "Linux":
    from pathlib import Path

import plotly.express as px
from plotly_resampler import FigureResampler

pio.templates.default = "plotly_white"

import tkinter as tk
from tkinter import filedialog

# Page Settings:
st.set_page_config(page_title="Paineira Real Time Plot", page_icon="🌳", layout="wide")


def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(master=root)
    root.destroy()
    return folder_path


with st.sidebar:
    selected_folder_path = st.session_state.get("folder_path", None)
    folder_select_button = st.button("Select Folder")
    if folder_select_button:
        selected_folder_path = select_folder()
        st.session_state.folder_path = selected_folder_path

    if selected_folder_path:
        st.write("Selected folder path:", selected_folder_path)

    # st.write('Select three known variables:')
    option = st.radio("Select file type:", ["All", "Other"])

    if option == "All":
        file_type = "*"
    if option == "Other":
        file_type = str(st.text_input("Which pattern?", "RAMP"))
        st.write(f"Only plot files with {file_type} on name.")

    step = int(st.text_input("Step used to plot all spectra:", 1))

    plot_title = str(st.text_input("Plot title:", "LaSrTiNiO"))

    temperature_range = st.sidebar.slider(
        label="Select temperature range:",
        min_value=0.0,
        max_value=1000.0,
        value=(124.0, 1000.0),
        step=0.1,
    )

    temp_min = temperature_range[0]
    temp_max = temperature_range[1]

    slider_option = st.radio("Show slider?", ["Yes", "Hide"])
    if slider_option == "Yes":
        show_slider = True
    if slider_option == "Hide":
        show_slider = False

    file_name = str(st.text_input("File name to save:", "beutiful_plot_from_paineira"))


def fix_temp(x):
    """Obtain the fixed temperature of the blower

    Args:
        x (float): temperature in Celcius degree

    Returns:
        flaot: fixed temperature of empirical model
    """
    if x <= 124.9:
        return x
    else:
        x = x + 273.15  # Convert to Kelvin
        x = (x - 85.28) / 1.0593
        return x - 273.15  # Revert to Celcius degree


path = Path(selected_folder_path)  # Folder location
file_option = file_type  # Select the pattern
file_path = str(path / f"*{file_option}*.csv")
files = glob(file_path, recursive=True)  # Find all files in the folder
df = pd.DataFrame(files, columns=["file_path"])  # Convert files to a Pandas DataFrame
df["file_path"] = df["file_path"].apply(Path)  # Convert each line to a Path-like object
df["file_name"] = df["file_path"].apply(
    lambda x: x.name
)  # Obtain the name of each file
df["temp"] = (
    df["file_name"].str.split("Celsius").str[0].str.split("_").str[-1].astype(float)
)  # Obtain temperature from file name
df["fixed_temp"] = df["temp"].apply(fix_temp)  # Fix the temperature
df["data"] = df["file_path"].apply(
    lambda x: pd.read_csv(x)
)  # Read all files. This operation might take a while


# df = df.sort_values(by='fixed_temp', ascending=True).reset_index(drop=True) # Sort values by temperature
df = (
    df.sort_values(by="fixed_temp", ascending=True)
    .query(f"fixed_temp>={temp_min} and fixed_temp<={temp_max}")
    .reset_index(drop=True)
)  # Same as above, but use only fixed temperature.


# Drop rows based on step
if step in [0, 1]:
    df_step = df
else:
    df_step = df.iloc[pd.RangeIndex(0, len(df), step)].reset_index(drop=True)


# Plot options
n_colors = len(df_step)
colors = px.colors.sample_colorscale(
    "turbo", [n / (n_colors - 1) for n in range(n_colors)]
)
config = {
    "toImageButtonOptions": {
        "format": "png",
        "filename": f"{file_name}",
        "height": None,
        "width": None,
        "scale": 6,
    }
}


fig = FigureResampler(go.Figure())
y = 0
for i, n in enumerate(range(0, len(df_step))):
    temp = df_step.iloc[n]["fixed_temp"]
    data = df_step.iloc[n]["data"]
    temp = np.repeat(temp, len(data))
    theta = data["2theta (degree)"]
    intensity = data["Intensity"] / max(data["Intensity"]) + y
    y = y + 0.15
    fig.add_traces(
        go.Scatter(x=theta, y=intensity, mode="markers+lines", marker_color=colors[i])
    )
fig.update_layout(
    yaxis_title="Intensity [arb. unit]",
    xaxis_title=r"$2\theta$ [$^\circ$]",
    title=plot_title,
    showlegend=False,
    font=dict(size=18),
    yaxis=dict(tickmode="array", tickvals=[], ticktext=[]),
)
colorbar_trace = go.Scatter(
    x=[None],
    y=[None],
    mode="markers",
    marker=dict(
        colorscale=colors,
        showscale=True,
        cmin=df_step.fixed_temp.min(),
        cmax=df_step.fixed_temp.max(),
        colorbar=dict(thickness=5),
    ),
    hoverinfo="none",
)
fig.add_trace(colorbar_trace)
fig.update_layout(
    autosize=True,
    height=600,
)
if show_slider:
    fig.update_xaxes(rangeslider_visible=True)

st.components.v1.html(fig.to_html(include_mathjax="cdn", config=config), height=1000)
# st.plotly_chart(fig, use_container_width=True)
