import pytest
import pandas as pd
import numpy as np
from tiled.adapters.mapping import MapAdapter
from tiled.adapters.xarray import DatasetAdapter
from tiled.client import Context, from_context
from tiled.server.app import build_app


# Tiled data to use for testing
# Some mocked test data
run1 = pd.DataFrame(
    {
        "energy_energy": np.linspace(8300, 8400, num=100),
        "It_net_counts": np.abs(np.sin(np.linspace(0, 4 * np.pi, num=100))),
        "I0_net_counts": np.linspace(1, 2, num=100),
    }
).to_xarray()

grid_scan = pd.DataFrame(
    {
        "CdnIPreKb": np.linspace(0, 104, num=105),
        "It_net_counts": np.linspace(0, 104, num=105),
        "aerotech_horiz": np.linspace(0, 104, num=105),
        "aerotech_vert": np.linspace(0, 104, num=105),
    }
).to_xarray()

hints = {
    "energy": {"fields": ["energy_energy", "energy_id_energy_readback"]},
}

bluesky_mapping = {
    "7d1daf1d-60c7-4aa7-a668-d1cd97e5335f": MapAdapter(
        {
            "primary": MapAdapter(
                {
                    "data": DatasetAdapter.from_dataset(run1),
                },
                metadata={"descriptors": [{"hints": hints}]},
            ),
        },
        metadata={
            "plan_name": "xafs_scan",
            "start": {
                "plan_name": "xafs_scan",
                "uid": "7d1daf1d-60c7-4aa7-a668-d1cd97e5335f",
                "hints": {"dimensions": [[["energy_energy"], "primary"]]},
            },
        },
    ),
    "9d33bf66-9701-4ee3-90f4-3be730bc226c": MapAdapter(
        {
            "primary": MapAdapter(
                {
                    "data": DatasetAdapter.from_dataset(run1),
                },
                metadata={"descriptors": [{"hints": hints}]},
            ),
        },
        metadata={
            "start": {
                "plan_name": "rel_scan",
                "uid": "9d33bf66-9701-4ee3-90f4-3be730bc226c",
                "hints": {"dimensions": [[["pitch2"], "primary"]]},
            }
        },
    ),
    # 2D grid scan map data
    "85573831-f4b4-4f64-b613-a6007bf03a8d": MapAdapter(
        {
            "primary": MapAdapter(
                {
                    "data": DatasetAdapter.from_dataset(grid_scan),
                },
                metadata={
                    "descriptors": [
                        {
                            "hints": {
                                "Ipreslit": {"fields": ["Ipreslit_net_counts"]},
                                "CdnIPreKb": {"fields": ["CdnIPreKb_net_counts"]},
                                "I0": {"fields": ["I0_net_counts"]},
                                "CdnIt": {"fields": ["CdnIt_net_counts"]},
                                "aerotech_vert": {"fields": ["aerotech_vert"]},
                                "aerotech_horiz": {"fields": ["aerotech_horiz"]},
                                "Ipre_KB": {"fields": ["Ipre_KB_net_counts"]},
                                "CdnI0": {"fields": ["CdnI0_net_counts"]},
                                "It": {"fields": ["It_net_counts"]},
                            }
                        }
                    ]
                },
            ),
        },
        metadata={
            "start": {
                "plan_name": "grid_scan",
                "uid": "85573831-f4b4-4f64-b613-a6007bf03a8d",
                "hints": {
                    "dimensions": [
                        [["aerotech_vert"], "primary"],
                        [["aerotech_horiz"], "primary"],
                    ],
                    "gridding": "rectilinear",
                },
                "shape": [5, 21],
                "extents": [[-80, 80], [-100, 100]],
            },
        },
    ),
}


mapping = {
    "255id_testing": MapAdapter(bluesky_mapping),
}

tree = MapAdapter(mapping)


@pytest.fixture(scope="session")
def tiled_client():
    app = build_app(tree)
    with Context.from_app(app) as context:
        client = from_context(context)
        yield client["255id_testing"]
