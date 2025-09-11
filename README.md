# Renderer

This repository contains a small Streamlit application that converts `.clqtt` subtitle files to numbered HTML and a CSV containing any annotations found in the input.  

## Setup

Install the dependencies using pip:

```bash
pip install -r requirements.txt
```

Run the app with:

```bash
streamlit run Renderer.py
```

This will start a local Streamlit server where you can upload a `.clqtt` file and download the generated HTML and CSV.

## Running Tests

```
pytest
```
