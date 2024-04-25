import platform
from glob import glob

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

if platform.system() == "Windows":
    from pathlib import PureWindowsPath as Path
elif platform.system() == "Linux":
    from pathlib import Path

import plotly.express as px
from matplotlib import rcParams
from plotly_resampler import FigureResampler
    "font.size": 22,
    "pgf.texsystem": "pdflatex",
    "font.family": "serif",
    "text.usetex": True,
}
rcParams.update(config)

pio.templates.default = "plotly_white"

# Options:
file_type = {
    "all": "*",
    "pattern": "_RAMP_",
}
folder_location = "..\\final_aggregate_files\\"
# folder_location = 'Z:\\lnls\\beamlines\\paineira\\proposals\\20240869\\proc\\pimega_450d\\2024\\april\lstn_650_h2flow_pc\\final_aggregate_files\\'
step = 1
plot_title = "LaSrTiNiO"
temp_min = 124.9
temp_max = 1000  # None
show_slider = True
file_name = "new_plot"


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


path = Path(folder_location)  # Folder location
file_option = file_type["pattern"]  # Select the pattern
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
        go.Scatter(x=theta, y=intensity, mode="lines", marker_color=colors[i])
    )
fig.update_layout(
    yaxis_title="Intensity [arb. unit]",
    xaxis_title=r"$2\theta$ [$^\circ$]",
    title=plot_title,
    showlegend=False,
    font=dict(size=18),
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
if show_slider:
    fig.update_xaxes(rangeslider_visible=True)
fig.show(config=config)
