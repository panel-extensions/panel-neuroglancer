import panel as pn
import neuroglancer

pn.extension()
class NeuroglancerNB(pn.viewable.Viewer):
    """
    A HoloViz Panel app for visualizing and interacting with Neuroglancer viewers
    within a Jupyter Notebook.

    This app supports loading from a parameterized Neuroglancer URL or an existing
    `neuroglancer.viewer.Viewer` instance.
    """

    DEMO_URL = "https://neuroglancer-demo.appspot.com/#!%7B%22dimensions%22%3A%7B%22x%22%3A%5B6.000000000000001e-9%2C%22m%22%5D%2C%22y%22%3A%5B6.000000000000001e-9%2C%22m%22%5D%2C%22z%22%3A%5B3.0000000000000004e-8%2C%22m%22%5D%7D%2C%22position%22%3A%5B5029.42333984375%2C6217.5849609375%2C1182.5%5D%2C%22crossSectionScale%22%3A3.7621853549999242%2C%22projectionOrientation%22%3A%5B-0.05179581791162491%2C-0.8017329573631287%2C0.0831851214170456%2C-0.5895944833755493%5D%2C%22projectionScale%22%3A4699.372698097029%2C%22layers%22%3A%5B%7B%22type%22%3A%22image%22%2C%22source%22%3A%22precomputed%3A%2F%2Fgs%3A%2F%2Fneuroglancer-public-data%2Fkasthuri2011%2Fimage%22%2C%22tab%22%3A%22source%22%2C%22name%22%3A%22original-image%22%7D%2C%7B%22type%22%3A%22image%22%2C%22source%22%3A%22precomputed%3A%2F%2Fgs%3A%2F%2Fneuroglancer-public-data%2Fkasthuri2011%2Fimage_color_corrected%22%2C%22tab%22%3A%22source%22%2C%22name%22%3A%22corrected-image%22%7D%2C%7B%22type%22%3A%22segmentation%22%2C%22source%22%3A%22precomputed%3A%2F%2Fgs%3A%2F%2Fneuroglancer-public-data%2Fkasthuri2011%2Fground_truth%22%2C%22tab%22%3A%22source%22%2C%22selectedAlpha%22%3A0.63%2C%22notSelectedAlpha%22%3A0.14%2C%22segments%22%3A%5B%223208%22%2C%224901%22%2C%2213%22%2C%224965%22%2C%224651%22%2C%222282%22%2C%223189%22%2C%223758%22%2C%2215%22%2C%224027%22%2C%223228%22%2C%22444%22%2C%223207%22%2C%223224%22%2C%223710%22%5D%2C%22name%22%3A%22ground_truth%22%7D%5D%2C%22layout%22%3A%224panel%22%7D"

    def __init__(
        self,
        source=None,
        aspect_ratio=2.75,
        show_state=False,
        load_demo=False,
        **params,
    ):
        """
        Initializes the NeuroglancerNB app.

        Parameters
        ----------
        source : str or neuroglancer.viewer.Viewer, optional
            Source for the initial state of the viewer, which can be a URL string or an existing `neuroglancer.viewer.Viewer` instance.
            If None, a new viewer will be initialized without a predefined state.
        aspect_ratio : float, optional
            The width-to-height ratio for the window-responsive Neuroglancer viewer. Default is 2.75.
        show_state : bool, optional
            Provides a collapsible card widget under the viewer that displays the viewer's state.
            Useful for debugging. Default is False.
        load_demo : bool, optional
            If True, loads the demo dataset upon initialization. Default is False.
        **params
            Additional parameters passed to the parent class.
        """
        super().__init__(**params)
        self.source_not_provided = False if source else True
        self.show_state = show_state
        self.viewer = (
            source
            if isinstance(source, neuroglancer.viewer.Viewer)
            else neuroglancer.Viewer()
        )

        self._setup_ui_components(aspect_ratio=aspect_ratio)
        self._configure_viewer()
        self._setup_callbacks()

        if source and not isinstance(source, neuroglancer.viewer.Viewer):
            self._initialize_viewer_from_url(source)

        if load_demo:
            self.demo_button.clicks += 1

    def _initialize_viewer_from_url(self, source: str):
        self.url_input.value = source
        self._load_state_from_url(source)

    def _setup_ui_components(self, aspect_ratio):
        self.url_input = pn.widgets.TextInput(
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
            {}, theme="light", depth=2, name="Viewer State", height=800, width=350
        )

        self.shareable_url_pane = pn.pane.Markdown("**Shareable URL:**")
        self.local_url_pane = pn.pane.Markdown("**Local URL:**")

        self.iframe = pn.pane.HTML(
            sizing_mode="stretch_both",
            aspect_ratio=aspect_ratio,
            min_height=800,
            styles={"resize": "both", "overflow": "hidden"},
        )

    def _configure_viewer(self):
        self._update_local_url()
        self._update_iframe_with_local_url()

    def _setup_callbacks(self):
        self.load_button.on_click(self._on_load_button_clicked)
        self.demo_button.on_click(self._on_demo_button_clicked)
        self.viewer.shared_state.add_changed_callback(self._on_viewer_state_changed)

    def _on_demo_button_clicked(self, event):
        self.url_input.value = self.DEMO_URL
        self._load_state_from_url(self.url_input.value)

    def _on_load_button_clicked(self, event):
        self._load_state_from_url(self.url_input.value)

    def _load_state_from_url(self, url):
        try:
            new_state = self._parse_state_from_url(url)
            self.viewer.set_state(new_state)
        except Exception as e:
            print(f"Error loading Neuroglancer state: {e}")

    def _parse_state_from_url(self, url):
        return neuroglancer.parse_url(url)

    def _on_viewer_state_changed(self):
        self._update_shareable_url()
        self._update_json_pane()

    def _update_shareable_url(self):
        shareable_url = neuroglancer.to_url(self.viewer.state)
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
        # only visible if no source is provided
        controls_layout = pn.Column(
            pn.Row(self.demo_button, self.load_button),
            pn.Row(self.url_input),
            visible=self.source_not_provided,
        )
        links_layout = pn.Column(self.local_url_pane, self.shareable_url_pane)

        state_widget = pn.Card(
                self.json_pane,
                title="State",
                collapsed=False,
                visible=self.show_state,
                styles={"background": "WhiteSmoke"},
                max_width=350
            )
        return pn.Column(
            controls_layout,
            links_layout,
            pn.Row(state_widget, self.iframe))
