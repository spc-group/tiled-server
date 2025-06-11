import numpy as np
import pandas as pd
import pytest
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
    "monochromator": {
        "data": {
            "monochromator-d_spacing": 3.13,
        },
        "data_keys": {
            "monochromator-d_spacing": {
                "dtype": "number",
                "dtype_numpy": "<f8",
                "shape": [],
                "source": "ca://255idbNP:d_spacing",
            },
        },
    }
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
}


baseline_data_keys = {
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
    "no_device": {},  # Make sure we test a device with no hints
}


@pytest.fixture
def tree(tmpdir):
    return in_memory(writable_storage=str(tmpdir))


@pytest.fixture()
def xafs_run(tree):
    with Context.from_app(build_app(tree)) as context:
        client = from_context(context)
        # Write sample data
        streams = client.create_container("streams")
        primary_metadata = {
            "hints": hints,
            "data_keys": data_keys,
            "configuration": xafs_config,
        }
        primary = streams.create_composite("primary", metadata=primary_metadata)
        internal = primary.write_dataframe(xafs_events, key="internal")
        # Fluorescence data
        primary.write_array(np.zeros(shape=(100, 8, 4096)), key="ge_8element")
        primary.write_array(np.ones(shape=(100,)), key="ge_8element-element0-all_event")
        # internal.write_dataframe(xafs_events, key="events")
        baseline = streams.create_composite(
            "baseline",
            metadata={
                "hints": {"aps_current": {"fields": ["aps_current"]}},
                "data_keys": baseline_data_keys,
            },
        )
        internal = baseline.write_dataframe(xafs_baseline, key="internal")
        yield tree
