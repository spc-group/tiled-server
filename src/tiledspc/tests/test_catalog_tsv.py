import datetime
import io

import pandas as pd
import pytest
import pytest_asyncio

from tiledspc.serialization.tsv import build_xdi, serialize_xdi, serialize_tsv

# <BlueskyRun({'primary'})>
metadata = {
    "start": {
        "detectors": ["I0"],
        "edge": "Ni_K",
        "hints": {"dimensions": [[["pitch2"], "primary"]]},
        "facility_id": "Advanced Photon Source",
        "beamline_id": "255-ID-Z",
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


@pytest_asyncio.fixture()
async def xdi_text(xafs_run):
    # Generate the headers
    xdi_text = await serialize_xdi(
        node=xafs_run,
        metadata=metadata,
        filter_for_access=None,
    )
    return xdi_text.decode("utf-8")


@pytest_asyncio.fixture()
async def tsv_text(xafs_run):
    # Generate the headers
    tsv_text = await serialize_tsv(
        node=xafs_run,
        metadata=metadata,
        filter_for_access=None,
    )
    return tsv_text.decode("utf-8")


def test_required_headers(xdi_text):
    assert "# XDI/1.0 bluesky/1.9.0 ophyd/1.7.0" in xdi_text
    assert "# Column.1: energy eV" in xdi_text
    assert "# Column.2: It-net_current A" in xdi_text
    assert "# Element.symbol: Ni" in xdi_text
    assert "# Element.edge: K" in xdi_text
    assert "# Mono.d_spacing: 3" in xdi_text  # Not implemented yet
    assert "# -------------" in xdi_text


def test_optional_headers(xdi_text):
    expected_metadata = {
        "Facility.name": "Advanced Photon Source",
        # "Facility.xray_source": "insertion device",
        "Beamline.name": "255-ID-Z",
        "Scan.start_time": "2022-10-06 09:14:57-0500",
        "uid": "7d1daf1d-60c7-4aa7-a668-d1cd97e5335f",
    }
    for key, val in expected_metadata.items():
        assert f"# {key.lower()}: {val.lower()}\n" in xdi_text.lower()


def test_tsv_headers(tsv_text):
    """Do we still get a valid TSV file without any metadata."""
    assert "# energy\tIt-net_current" in tsv_text
    assert "d_spacing" not in tsv_text
    # Check the data
    buff = io.StringIO(tsv_text)
    df = pd.read_csv(buff, comment="#", sep="\t")
    assert len(df.columns) == 2


def test_data(xdi_text):
    """Check that the TSV data section is present and correct."""
    # Read as if it were a pandas dataframe
    buff = io.StringIO(xdi_text)
    # Check for the header
    assert "# energy\tIt-net_current" in xdi_text
    # Check the data
    df = pd.read_csv(buff, comment="#", sep="\t")
    assert len(df.columns) == 2
