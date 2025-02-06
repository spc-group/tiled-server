import datetime
import io

import h5py
import pytest

from tiledspc.serialization.container import serialize_nexus

# <BlueskyRun({'primary'})>
metadata = {
    "start": {
        "detectors": ["I0"],
        "hints": {"dimensions": [[["pitch2"], "primary"]]},
        "motors": ["pitch2"],
        "num_intervals": 19,
        "num_points": 20,
        "plan_args": {
            "args": [
                "EpicsMotor(prefix='25idDCM:AS:m6', "
                "name='pitch2', settle_time=0.0, "
                "timeout=None, read_attrs=['user_readback', "
                "'user_setpoint'], "
                "configuration_attrs=['user_offset', "
                "'user_offset_dir', 'velocity', "
                "'acceleration', 'motor_egu'])",
                -100,
                100,
            ],
            "detectors": [
                "IonChamber(prefix='25idcVME:3820:scaler1', "
                "name='I0', read_attrs=['raw_counts'], "
                "configuration_attrs=[])"
            ],
            "num": 20,
            "per_step": "None",
        },
        "plan_name": "rel_scan",
        "plan_pattern": "inner_product",
        "plan_pattern_args": {
            "args": [
                "EpicsMotor(prefix='25idDCM:AS:m6', "
                "name='pitch2', settle_time=0.0, "
                "timeout=None, "
                "read_attrs=['user_readback', "
                "'user_setpoint'], "
                "configuration_attrs=['user_offset', "
                "'user_offset_dir', 'velocity', "
                "'acceleration', 'motor_egu'])",
                -100,
                100,
            ],
            "num": 20,
        },
        "plan_pattern_module": "bluesky.plan_patterns",
        "plan_type": "generator",
        "purpose": "alignment",
        "scan_id": 1,
        "time": 1665065697.3635247,
        "uid": "7d1daf1d-60c7-4aa7-a668-d1cd97e5335f",
        "versions": {"bluesky": "1.9.0", "ophyd": "1.7.0"},
    },
    "stop": {
        "exit_status": "success",
        "num_events": {"primary": 20},
        "reason": "",
        "run_start": "7d1daf1d-60c7-4aa7-a668-d1cd97e5335f",
        "time": 1665065735.714015,
        "uid": "c1eac86f-d568-41a1-b601-a0e2fd6ed55e",
    },
    "summary": {
        "datetime": datetime.datetime(2022, 10, 6, 9, 14, 57, 363525),
        "duration": 38.35049033164978,
        "plan_name": "rel_scan",
        "scan_id": 1,
        "stream_names": ["primary"],
        "timestamp": 1665065697.3635247,
        "uid": "7d1daf1d-60c7-4aa7-a668-d1cd97e5335f",
    },
}


@pytest.mark.asyncio
async def test_file_structure(tiled_client):
    uid = "7d1daf1d-60c7-4aa7-a668-d1cd97e5335f"
    container = tiled_client[uid]
    # Perform the serialization
    buff = await serialize_nexus(container, metadata, filter_for_access=None)
    buff = io.BytesIO(buff.tobytes())
    with h5py.File(buff) as fp:
        # Check the top-level entry
        assert fp.attrs["default"] == uid
        assert uid in fp.keys()
        entry = fp[uid]
        assert entry.attrs["NX_class"] == "NXentry"
        assert entry.attrs["default"] == "primary"
        # Check the default data group
        assert "primary" in entry.keys()
        primary = entry["primary"]
        assert primary.attrs["NX_class"] == "NXdata"
        # assert primary.attrs["signal"] == ""
        # assert primary.attrs["axes"] == ""
        # Check some of the run columns
        assert "energy_energy" in primary.keys()
        assert primary["energy_energy"].shape == (100,)
        assert "It_net_counts" in primary.keys()
        assert "I0_net_counts" in primary.keys()
        assert primary["energy_energy"].attrs["NX_class"] == "NXdata"
        # assert False, primary['energy_energy']
