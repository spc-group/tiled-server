import datetime
import io
from unittest import mock

import pytest
import pytest_asyncio

from tiledspc.serialization.nexus import NexusIO, serialize_nexus, write_stream

specification = """
root:NXroot
  @default = '7d1daf1d-60c7-4aa7-a668-d1cd97e5335f'
  7d1daf1d-60c7-4aa7-a668-d1cd97e5335f:NXentry
    data:NXdata
      It-net_current -> /7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrument/bluesky/streams/primary/It-net_current/value
      energy -> /7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrument/bluesky/streams/primary/energy/value
      energy-id-energy-readback -> /7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrument/bluesky/streams/primary/energy-id-energy-readback/value
      ge_8element -> /7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrument/bluesky/streams/primary/ge_8element/value
    duration = 38.35049033164978
    entry_identifier -> /7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrument/bluesky/metadata/start.uid
    instrument:NXinstrument
      bluesky:NXnote
        metadata:NXnote
          start.detectors = '["I0"]'
          start.hints = '{"dimensions": [[["pitch2"], "primary"]]}'
          start.motors = '["pitch2"]'
          start.num_intervals = 19
          start.num_points = 20
          start.plan_args = '{"args": ["EpicsMotor(prefix='25idDCM:AS:m6', name='pitc...'
          start.plan_name = 'rel_scan'
            @target = '/7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrume...'
          start.plan_pattern = 'inner_product'
          start.plan_pattern_args = '{"args": ["EpicsMotor(prefix='25idDCM:AS:m6', name='pitc...'
          start.plan_pattern_module = 'bluesky.plan_patterns'
          start.plan_type = 'generator'
          start.purpose = 'alignment'
          start.sample_name = 'NMC-811'
            @target = '/7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrume...'
          start.scan_id = 1
          start.scan_name = 'Pristine'
            @target = '/7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrume...'
          start.time = 1665065697.3635247
          start.uid = '7d1daf1d-60c7-4aa7-a668-d1cd97e5335f'
            @target = '/7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrume...'
          start.versions = '{"bluesky": "1.9.0", "ophyd": "1.7.0"}'
          stop.exit_status = 'success'
          stop.num_events = '{"primary": 20}'
          stop.reason = ''
          stop.run_start = '7d1daf1d-60c7-4aa7-a668-d1cd97e5335f'
          stop.time = 1665065735.714015
          stop.uid = 'c1eac86f-d568-41a1-b601-a0e2fd6ed55e'
          summary.datetime = '2022-10-06 09:14:57.363525'
          summary.duration = 38.35049033164978
          summary.plan_name = 'rel_scan'
          summary.scan_id = 1
          summary.stream_names = '["primary"]'
          summary.timestamp = 1665065697.3635247
          summary.uid = '7d1daf1d-60c7-4aa7-a668-d1cd97e5335f'
        plan_name -> /7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrument/bluesky/metadata/start.plan_name
        streams:NXnote
          baseline:NXnote
            aps_current:NXdata
              @axes = 'time'
              @signal = 'value'
              EPOCH = [10 25]
              time = [ 0 15]
                @units = 's'
              value = [130.  204.1]
                @units = 'mA'
            aps_fill_number:NXdata
              @axes = 'time'
              @signal = 'value'
              EPOCH = [10 25]
              time = [ 0 15]
                @units = 's'
              value = [1 2]
            aps_global_feedback:NXdata
              @axes = 'time'
              @signal = 'value'
              EPOCH = [10 25]
              time = [ 0 15]
                @units = 's'
              value = [ True False]
          primary:NXnote
            I0-net_current:NXdata
              @axes = 'time'
              @signal = 'value'
              EPOCH = float64(100)
              time = float64(100)
                @units = 's'
              value = float64(100)
                @units = 'A'
            It-net_current:NXdata
              @axes = 'time'
              @signal = 'value'
              EPOCH = float64(100)
              time = float64(100)
                @units = 's'
              value = float64(100)
                @target = '/7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrume...'
                @units = 'A'
            energy:NXdata
              @axes = 'time'
              @signal = 'value'
              EPOCH = float64(100)
              time = float64(100)
                @units = 's'
              value = float64(100)
                @target = '/7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrume...'
                @units = 'eV'
            energy-id-energy-readback:NXdata
              @axes = 'time'
              @signal = 'value'
              EPOCH = float64(100)
              time = float64(100)
                @units = 's'
              value = float64(100)
                @target = '/7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrume...'
                @units = 'keV'
            ge_8element:NXdata
              value = float64(100x8x4096)
                @target = '/7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrume...'
            ge_8element-element0-all_event:NXdata
              value = float64(100)
        uid -> /7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrument/bluesky/metadata/start.uid
    plan_name -> /7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrument/bluesky/metadata/start.plan_name
    sample_name -> /7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrument/bluesky/metadata/start.sample_name
    scan_name -> /7d1daf1d-60c7-4aa7-a668-d1cd97e5335f/instrument/bluesky/metadata/start.scan_name
    start_time = '2022-10-06T09:14:57.363525-05:00'
    stop_time = '2022-10-06T09:15:35.714015-05:00'
"""


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
        "sample_name": "NMC-811",
        "scan_name": "Pristine",
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
async def nxfile(xafs_run):
    # Generate the headers
    buff = bytes(
        await serialize_nexus(xafs_run, metadata=metadata, filter_for_access=None)
    )
    buff = io.BytesIO(buff)
    with NexusIO(buff, mode="r") as fd:
        # Write data entry to the nexus file
        yield fd


@pytest.mark.asyncio
async def test_xafs_specification(nxfile):
    tree = nxfile.readfile().tree
    # with open("/home/beams/WOLFMAN/tmp/test_file.tree", mode='w') as fd:
    #     fd.write(tree)
    tree = "\n" + tree + "\n"  # Extra newlines to match the triple quote string
    assert tree == specification


@pytest.mark.asyncio
async def test_file_structure(nxfile):
    uid = "7d1daf1d-60c7-4aa7-a668-d1cd97e5335f"
    # Check the top-level entry
    assert nxfile.attrs["default"] == uid
    assert uid in nxfile.keys()
    entry = nxfile[uid]
    assert entry.attrs["NX_class"] == "NXentry"


@pytest.mark.asyncio
async def test_missing_hints(xafs_run):
    """Make sure the stream still writes if there are not hints."""
    await write_stream(
        name="primary",
        node=mock.AsyncMock(),
        nxentry=mock.MagicMock(),
        metadata={
            "data_keys": {},
            "hints": {"I0": {}},
        },
    )
