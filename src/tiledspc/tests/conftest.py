import numpy as np
import pandas as pd
import pytest
from tiled.adapters.mapping import MapAdapter
from tiled.adapters.table import TableAdapter
from tiled.catalog import in_memory
from tiled.client import Context, from_context
from tiled.server.app import build_app

# Tiled data to use for testing
# Some mocked test data
xafs_events = pd.DataFrame(
    {
        "energy": np.linspace(8300, 8400, num=100),
        "energy-id-energy-readback": np.linspace(8.32, 8.42, num=100),
        "ts_energy": np.linspace(0, 15, num=100),
        "ts_energy-id-energy-readback": np.linspace(0, 15, num=100),
        "It-net_current": np.abs(np.sin(np.linspace(0, 4 * np.pi, num=100))),
        "ts_It-net_current": np.linspace(0, 15, num=100),
        "I0-net_current": np.linspace(1, 2, num=100),
        "ts_I0-net_current": np.linspace(0, 15, num=100),
    }
)

xafs_baseline = pd.DataFrame(
    {
        "aps_current": np.asarray([130.0, 204.1]),
        "aps_fill_number": np.asarray([1, 2]),
        "aps_global_feedback": np.asarray([True, False]),
        "ts_aps_current": np.asarray([10, 25]),
        "ts_aps_fill_number": np.asarray([10, 25]),
        "ts_aps_global_feedback": np.asarray([10, 25]),
    }
)

xafs_config = {
    "energy": pd.DataFrame(
        {
            "energy-monochromator-d_spacing": [3.13],
        }
    )
}

grid_scan = pd.DataFrame(
    {
        "CdnIPreKb": np.linspace(0, 104, num=105),
        "It_net_counts": np.linspace(0, 104, num=105),
        "aerotech_horiz": np.linspace(0, 104, num=105),
        "aerotech_vert": np.linspace(0, 104, num=105),
    }
)

data_keys = {
    "energy": {
        "dtype": "number",
        "dtype_numpy": "<f8",
        "limits": {
            "control": {"high": 0.0, "low": 0.0},
            "display": {"high": 0.0, "low": 0.0},
        },
        "object_name": "energy",
        "precision": 3,
        "shape": [],
        "source": "ca://25idcVME:3820:scaler1.T",
        "units": "eV",
    },
    "energy-id-energy-readback": {
        "dtype": "number",
        "dtype_numpy": "<f8",
        "limits": {
            "control": {"high": 0.0, "low": 0.0},
            "display": {"high": 0.0, "low": 0.0},
        },
        "object_name": "energy",
        "precision": 3,
        "shape": [],
        "source": "ca://...",
        "units": "keV",
    },
    # "I0-mcs-scaler-channels-0-net_count": {
    #     "dtype": "number",
    #     "dtype_numpy": "<f8",
    #     "limits": {
    #         "control": {"high": 0.0, "low": 0.0},
    #         "display": {"high": 0.0, "low": 0.0},
    #     },
    #     "object_name": "I0",
    #     "precision": 0,
    #     "shape": [],
    #     "source": "ca://25idcVME:3820:scaler1_netA.A",
    #     "units": "",
    # },
    # "I0-mcs-scaler-channels-3-net_count": {
    #     "dtype": "number",
    #     "dtype_numpy": "<f8",
    #     "limits": {
    #         "control": {"high": 0.0, "low": 0.0},
    #         "display": {"high": 0.0, "low": 0.0},
    #     },
    #     "object_name": "I0",
    #     "precision": 0,
    #     "shape": [],
    #     "source": "ca://25idcVME:3820:scaler1_netA.D",
    #     "units": "",
    # },
    # "I0-mcs-scaler-elapsed_time": {
    #     "dtype": "number",
    #     "dtype_numpy": "<f8",
    #     "limits": {
    #         "control": {"high": 0.0, "low": 0.0},
    #         "display": {"high": 0.0, "low": 0.0},
    #     },
    #     "object_name": "I0",
    #     "precision": 3,
    #     "shape": [],
    #     "source": "ca://25idcVME:3820:scaler1.T",
    #     "units": "",
    # },
    "I0-net_current": {
        "dtype": "number",
        "dtype_numpy": "<f8",
        "object_name": "I0",
        "shape": [],
        "source": "soft://I0-net_current(gain,count,clock_count,clock_frequency,counts_per_volt_second)",
        "units": "A",
    },
    "It-net_current": {
        "dtype": "number",
        "dtype_numpy": "<f8",
        "object_name": "It",
        "shape": [],
        "source": "soft://It-net_current(gain,count,clock_count,clock_frequency,counts_per_volt_second)",
        "units": "A",
    },
    "ge_8element": {
        "dtype": "array",
        "dtype_numpy": "<u4",
        "external": "STREAM:",
        "object_name": "ge_8element",
        "shape": [8, 4096],
        "source": "ca://XSP_Ge_8elem:HDF1:FullFileName_RBV",
    },
    "ge_8element-element0-all_event": {
        "dtype": "number",
        "dtype_numpy": "<f8",
        "external": "STREAM:",
        "object_name": "ge_8element",
        "shape": [],
        "source": "ca://XSP_Ge_8elem:HDF1:FullFileName_RBV",
    },
    # "sim_motor_2": {
    #     "dtype": "number",
    #     "dtype_numpy": "<f8",
    #     "limits": {
    #         "control": {"high": 32000.0, "low": -32000.0},
    #         "display": {"high": 32000.0, "low": -32000.0},
    #     },
    #     "object_name": "sim_motor_2",
    #     "precision": 5,
    #     "shape": [],
    #     "source": "ca://25idc:simMotor:m2.RBV",
    #     "units": "degrees",
    # },
}


baseline_data_keys = {
    # "aps_current": np.asarray([130.0, 204.1]),
    #     "aps_fill_number": np.asarray([1, 2]),
    #     "aps_global_feedback": np.asarray([True, False]),
    # }
    "aps_current": {
        "dtype": "number",
        "dtype_numpy": "<f8",
        "limits": {
            "control": {"high": 0.0, "low": 0.0},
            "display": {"high": 0.0, "low": 0.0},
        },
        "object_name": "aps",
        "precision": 3,
        "shape": [],
        "source": "ca://...",
        "units": "mA",
    },
    "aps_fill_number": {
        "dtype": "number",
        "dtype_numpy": "<u4",
        "limits": {
            "control": {"high": 0.0, "low": 0.0},
            "display": {"high": 0.0, "low": 0.0},
        },
        "object_name": "aps",
        "shape": [],
        "source": "ca://...",
    },
    "aps_global_feedback": {
        "dtype": "bool",
        "dtype_numpy": "|u1",
        "limits": {
            "control": {"high": 0.0, "low": 0.0},
            "display": {"high": 0.0, "low": 0.0},
        },
        "object_name": "aps",
        "shape": [],
        "source": "ca://...",
    },
}


hints = {
    "energy": {"fields": ["energy", "energy-id-energy-readback"]},
    "It": {"fields": ["It-net_current"]},
    "ge_8element": {"fields": ["ge_8element"]},
}

bluesky_mapping = {
    # "7d1daf1d-60c7-4aa7-a668-d1cd97e5335f": MapAdapter(
    #     {
    #         "primary": MapAdapter(
    #             {
    #                 "internal": MapAdapter({"events": TableAdapter.from_pandas(run1)}),
    #                 "config": MapAdapter(
    #                     {
    #                         "energy": TableAdapter.from_pandas(
    #                             pd.DataFrame(
    #                                 {
    #                                     "energy-monochromator-d_spacing": [3.13],
    #                                 }
    #                             )
    #                         ),
    #                     }
    #                 ),
    #             },
    #             metadata={"hints": hints, "data_keys": data_keys},
    #         ),
    #     },
    #     metadata={
    #         "plan_name": "xafs_scan",
    #         "start": {
    #             "plan_name": "xafs_scan",
    #             "uid": "7d1daf1d-60c7-4aa7-a668-d1cd97e5335f",
    #             "hints": {"dimensions": [[["energy"], "primary"]]},
    #         },
    #     },
    # ),
    # "9d33bf66-9701-4ee3-90f4-3be730bc226c": MapAdapter(
    #     {
    #         "primary": MapAdapter(
    #             {
    #                 "internal": MapAdapter(
    #                     {
    #                         "events": TableAdapter.from_pandas(run1),
    #                     }
    #                 ),
    #             },
    #             metadata={"hints": hints},
    #         ),
    #     },
    #     metadata={
    #         "start": {
    #             "plan_name": "rel_scan",
    #             "uid": "9d33bf66-9701-4ee3-90f4-3be730bc226c",
    #             "hints": {"dimensions": [[["pitch2"], "primary"]]},
    #         }
    #     },
    # ),
    # 2D grid scan map data
    "85573831-f4b4-4f64-b613-a6007bf03a8d": MapAdapter(
        {
            "primary": MapAdapter(
                {
                    "internal": MapAdapter(
                        {
                            "events": TableAdapter.from_pandas(grid_scan),
                        }
                    ),
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


@pytest.fixture
def tree(tmpdir):
    return in_memory(writable_storage=str(tmpdir))


@pytest.fixture()
def xafs_run(tree):
    with Context.from_app(build_app(tree)) as context:
        client = from_context(context)
        # Write sample data
        primary = client.create_container(
            "primary", metadata={"hints": hints, "data_keys": data_keys}
        )
        internal = primary.create_container("internal")
        internal.write_dataframe(xafs_events, key="events")
        baseline = client.create_container(
            "baseline", metadata={"hints": {}, "data_keys": baseline_data_keys}
        )
        internal = baseline.create_container("internal")
        internal.write_dataframe(xafs_baseline, key="events")
        # Fluorescence detector data
        external = primary.create_container("external")
        external.write_array(np.zeros(shape=(100, 8, 4096)), key="ge_8element")
        external.write_array(
            np.ones(shape=(100,)), key="ge_8element-element0-all_event"
        )
        config = primary.create_container("config")
        for key, cfg in xafs_config.items():
            config.write_dataframe(cfg, key=key)
        # Write a baseline stream
        yield tree
