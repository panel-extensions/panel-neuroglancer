> 👉 Check out an example workflow [here](https://examples.holoviz.org/gallery/volumetric_imaging/volumetric_imaging.html).

# `panel-neuroglancer`

Use HoloViz [`Panel`](https://panel.holoviz.org/) to integrate [Neuroglancer](https://www.github.com/google/neuroglancer) into Jupyter notebook workflows and applications for scientifically contextualized, reproducible, and extensible workflows involving large volumetric datasets, such as those from electron and fluorescent microscopy. See the [Overview](#overview) below for more explanation.

## Install

`pip install panel_neuroglancer`

## Usage

### Option 1 - Load from a neuroglancer url:

Either use `Neuroglancer(source=<URL>)` or just run `Neuroglancer()` and input the URL in the GUI:
![](assets/demo_fromurl.png)


### Option 2 - Load from `neuroglancer.Viewer` instance:

```python
import neuroglancer
import panel as pn
from panel_neuroglancer import Neuroglancer

pn.extension() # necessary for panel extensions to render in a notebook
viewer = neuroglancer.Viewer()

with viewer.txn() as s:
    # Add an image layer from a precomputed data source
    s.layers["image"] = neuroglancer.ImageLayer(
        source="precomputed://gs://neuroglancer-janelia-flyem-hemibrain/emdata/clahe_yz/jpeg",
    )
    # Add a segmentation layer
    s.layers["segmentation"] = neuroglancer.SegmentationLayer(
        source="precomputed://gs://neuroglancer-janelia-flyem-hemibrain/v1.1/segmentation",
    )
Neuroglancer(source=viewer, show_state=True)
```

![](assets/demo_fromviewer.png)

## Overview

**Volumetric imaging** refers to techniques that capture data in three dimensions, allowing researchers to visualize and analyze the internal structures of objects, including depth and spatial relationships. Unlike traditional 2D imaging, volumetric imaging provides a more comprehensive view of specimens.

One of the most powerful volumetric imaging techniques is **electron microscopy** ([EM](https://en.wikipedia.org/wiki/Electron_microscope)). EM uses a beam of electrons to create high-resolution images at the nanometer scale, enabling the exploration of fine structural details of biological specimens such as cells, tissues, and molecular structures. However, handling and visualizing the massive datasets generated by EM poses significant challenges due to their size and complexity.

### Introducing Neuroglancer

[Neuroglancer](https://github.com/google/neuroglancer) by Google is a WebGL-based viewer designed specifically for volumetric data, offering efficient handling of large-scale datasets through data streaming. Its key features include:

- **Interactive Visualization:** Smooth, real-time navigation through volumetric data.
- **Customizable Layers:** Support for raw images, segmented regions, and annotations.
- **Web-Based Interface:** Accessible directly from browsers without the need for specialized software.

Originally developed for neuroscience, Neuroglancer empowers researchers to explore complex 3D structures by tracing neural pathways, identifying cellular components, and annotating regions of interest.

### Integrating Neuroglancer with Jupyter Notebooks

While Neuroglancer is a powerful tool for exploring large volumes, it is typically used as a standalone application. Researchers often utilize **Jupyter Notebooks** to conduct reproducible research and combine code, data analysis, and visualizations.

By integrating Neuroglancer within Jupyter Notebooks using [HoloViz Panel](https://panel.holoviz.org/), researchers can:

- **Consolidate Workflow:** Keep code, data analysis, and visualization in a single environment.
- **Enhance Reproducibility:** Share notebooks that include both computational steps and interactive visualizations.
- **Facilitate Collaboration:** Allow collaborators to interact with the same data and visualizations within the notebook.

### Using HoloViz Panel for the Integration

By using HoloViz Panel, we can:

- Embed the Neuroglancer viewer directly within a notebook cell.
- Create interactive widgets and controls to manipulate and report the state of the viewer.
- Combine Neuroglancer views alongside other visualizations.

## Funding

- 2024: Chan Zuckerberg Initiative. Learn more in the [grant announcement](https://blog.bokeh.org/announcing-czi-funding-for-bokeh-for-bioscience-5f74426c011a).
