In order to run this dashbord, you might need to install some dependencies. I recommend you use virtual environments, such as, `conda` (or `mamba`) or `poetry`. To install the following packages you can either install with `conda install` command or `pip` install:

- Dependencies:
    - Python>=3.10
    - NumPy
    - Pandas
    - Plotly
    - Streamlit
    - plotly_resampler

To test this repository*:

1. Install `git` on Windows or Linux (if you have Linux, you probably already have it)!
1. Clone the repository
    ```bash
    git clone 
    cd dashbord-paineira
    ```
1. Activate your environment (e.g., `mamba activate <my environment>`)
1. Install the following packages:
    ```bash
    pip install numpy pandas plotly streamlit plotly_resampler
    ```
1. Run the script:
    ```bash
    streamlit run streamlit.py
    ```
4. Select the folder that contains the time-series
5. Select other options, and you are ready to go.

* I assume you already have a Python environment installed. I suggest you install all these packages in another environment to do not break your current dependencies.
