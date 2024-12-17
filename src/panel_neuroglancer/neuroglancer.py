from __future__ import annotations

import neuroglancer
import panel as pn
import param
from neuroglancer.viewer import Viewer
from panel.custom import PyComponent

DEMO_URL = "https://neuroglancer-demo.appspot.com/#!%7B%22dimensions%22%3A%7B%22x%22%3A%5B6.000000000000001e-9%2C%22m%22%5D%2C%22y%22%3A%5B6.000000000000001e-9%2C%22m%22%5D%2C%22z%22%3A%5B3.0000000000000004e-8%2C%22m%22%5D%7D%2C%22position%22%3A%5B5029.42333984375%2C6217.5849609375%2C1182.5%5D%2C%22crossSectionScale%22%3A3.7621853549999242%2C%22projectionOrientation%22%3A%5B-0.05179581791162491%2C-0.8017329573631287%2C0.0831851214170456%2C-0.5895944833755493%5D%2C%22projectionScale%22%3A4699.372698097029%2C%22layers%22%3A%5B%7B%22type%22%3A%22image%22%2C%22source%22%3A%22precomputed%3A%2F%2Fgs%3A%2F%2Fneuroglancer-public-data%2Fkasthuri2011%2Fimage%22%2C%22tab%22%3A%22source%22%2C%22name%22%3A%22original-image%22%7D%2C%7B%22type%22%3A%22image%22%2C%22source%22%3A%22precomputed%3A%2F%2Fgs%3A%2F%2Fneuroglancer-public-data%2Fkasthuri2011%2Fimage_color_corrected%22%2C%22tab%22%3A%22source%22%2C%22name%22%3A%22corrected-image%22%7D%2C%7B%22type%22%3A%22segmentation%22%2C%22source%22%3A%22precomputed%3A%2F%2Fgs%3A%2F%2Fneuroglancer-public-data%2Fkasthuri2011%2Fground_truth%22%2C%22tab%22%3A%22source%22%2C%22selectedAlpha%22%3A0.63%2C%22notSelectedAlpha%22%3A0.14%2C%22segments%22%3A%5B%223208%22%2C%224901%22%2C%2213%22%2C%224965%22%2C%224651%22%2C%222282%22%2C%223189%22%2C%223758%22%2C%2215%22%2C%224027%22%2C%223228%22%2C%22444%22%2C%223207%22%2C%223224%22%2C%223710%22%5D%2C%22name%22%3A%22ground_truth%22%7D%5D%2C%22layout%22%3A%224panel%22%7D"


class Neuroglancer(PyComponent):
    """
    Neuroglancer is a Panel component for visualizing and interacting with a Neuroglancer Viewer.

    The component can be initialized from a URL or a `neuroglancer.viewer.Viewer` instance.
    """

    show_state = param.Boolean(default=False, doc="""
        Provides a collapsible card widget under the viewer that displays the viewer's state.""")

    url = param.String(default=None, doc="""
        The URL public URL of the Neuroglancer Viewer.""")

    def __init__(
        self,
        source=None,
        load_demo=False,
        **params,
    ):
        viewer = None
        if isinstance(source, str):
            params['url'] = source
        elif isinstance(source, Viewer):
            params['url'] = source.get_viewer_url()
            viewer = source
        elif source is not None:
            raise ValueError('Neuroglancer source must be a URL or neuroglancer Viewer instance')
        self._source_not_provided = source is None
        super().__init__(**params)
        if viewer is None:
            viewer = neuroglancer.Viewer()
        self.viewer = viewer

        self._setup_ui_components()
        self._configure_viewer()
        self._setup_callbacks()

        if isinstance(source, str):
            self._load_state_from_url(source)
        if load_demo:
            self._load_demo()

    def _setup_ui_components(self):
        self.url_input = pn.widgets.TextInput.from_param(
            self.param.url,
            placeholder="Enter a Neuroglancer URL and click Load",
            name="Input URL",
            width=700,
        )

        self.load_button = pn.widgets.Button(
            name="Load", button_type="primary", width=75
        )
        self.demo_button = pn.widgets.Button(
            name="Demo", button_type="warning", width=75
        )

        self.json_pane = pn.pane.JSON(
            {}, theme="light", depth=2, name="Viewer State", sizing_mode='stretch_both'
        )

        self.shareable_url_pane = pn.pane.Markdown("**Shareable URL:**")
        self.local_url_pane = pn.pane.Markdown("**Local URL:**")

        self.iframe = pn.pane.HTML(
            sizing_mode="stretch_both",
            aspect_ratio=self.param.aspect_ratio,
            margin=0,
            min_height=800,
            styles={"resize": "both", "overflow": "hidden"},
        )

    def _configure_viewer(self):
        self._update_local_url()
        self._update_iframe_with_local_url()

    def _setup_callbacks(self):
        self.load_button.on_click(self._load_url)
        self.demo_button.on_click(self._load_demo)
        self.viewer.shared_state.add_changed_callback(self._on_viewer_state_changed)

    def _load_demo(self, event=None):
        self.url = DEMO_URL
        self._load_state_from_url(self.url)

    def _load_url(self, event=None):
        self._load_state_from_url(self.url)

    def _load_state_from_url(self, url):
        try:
            new_state = self._parse_state_from_url(url)
            self.viewer.set_state(new_state)
        except Exception as e:
            print(f"Error loading Neuroglancer state: {e}")  # noqa

    def _parse_state_from_url(self, url):
        return neuroglancer.parse_url(url)

    def _on_viewer_state_changed(self):
        self._update_shareable_url()
        self._update_json_pane()

    def _update_shareable_url(self):
        self.url = shareable_url = neuroglancer.to_url(self.viewer.state)
        self.shareable_url_pane.object = self._generate_dropdown_markup(
            "Shareable URL", shareable_url
        )

    def _update_local_url(self):
        self.local_url_pane.object = self._generate_dropdown_markup(
            "Local URL", self.viewer.get_viewer_url()
        )

    def _update_iframe_with_local_url(self):
        iframe_style = (
            'frameborder="0" scrolling="no" marginheight="0" marginwidth="0" '
            'style="width:100%; height:100%; min-width:500px; min-height:500px;"'
        )
        self.iframe.object = (
            f'<iframe src="{self.viewer.get_viewer_url()}" {iframe_style}></iframe>'
        )

    def _update_json_pane(self):
        self.json_pane.object = self.viewer.state.to_json()

    def _generate_dropdown_markup(self, title, url):
        return f"""
        <details>
            <summary><b>{title}:</b></summary>
            <a href="{url}" target="_blank">{url}</a>
        </details>
        """

    def __panel__(self):
        controls = pn.Column(
            pn.Row(self.demo_button, self.load_button, visible=self._source_not_provided),
            pn.Row(self.url_input, visible=self._source_not_provided),
            self.local_url_pane,
            self.shareable_url_pane
        )
        state_widget = pn.Card(
            self.json_pane,
            title="State",
            collapsed=False,
            visible=self.param.show_state,
            styles={"background": "WhiteSmoke"},
            max_width=350
        )
        return pn.Column(
            controls,
            pn.Row(state_widget, self.iframe),
        )
