import datetime
import io

import h5py
import pytest
import pytest_asyncio
from tiled.catalog.adapter import CatalogContainerAdapter

from tiledspc.serialization.nexus import serialize_nexus, NexusIO


specification = """
root:NXroot
  @default = '7d1daf1d-60c7-4aa7-a668-d1cd97e5335f'
  7d1daf1d-60c7-4aa7-a668-d1cd97e5335f:NXentry
    duration:NX_FLOAT64[] = [ ... ]
    end_time:NX_CHAR = 2019-05-02T17:45:48.078618
    entry_identifier --> /entry/instrument/bluesky/uid
    plan_name --> /entry/instrument/bluesky/metadata/plan_name
    program_name:NX_CHAR = bluesky
    start_time:NX_CHAR = 2019-05-02T17:45:33.937294
    title:NX_CHAR = tune_mr-S0108-2ffe4d8
    contact:NXuser
      affiliation --> /entry/instrument/bluesky/streams/baseline/bss_user_info_institution/value_start
      email --> /entry/instrument/bluesky/streams/baseline/bss_user_info_email/value_start
      facility_user_id --> /entry/instrument/bluesky/streams/baseline/bss_user_info_badge/value_start
      name --> /entry/instrument/bluesky/streams/baseline/bss_user_info_contact/value_start
      role:NX_CHAR = contact
    data:NXdata
      EPOCH --> /entry/instrument/bluesky/streams/primary/scaler0_time/time
      I0_USAXS --> /entry/instrument/bluesky/streams/primary/I0_USAXS/value
      m_stage_r --> /entry/instrument/bluesky/streams/primary/m_stage_r/value
      m_stage_r_soft_limit_hi --> /entry/instrument/bluesky/streams/primary/m_stage_r_soft_limit_hi/value
      m_stage_r_soft_limit_lo --> /entry/instrument/bluesky/streams/primary/m_stage_r_soft_limit_lo/value
      m_stage_r_user_setpoint --> /entry/instrument/bluesky/streams/primary/m_stage_r_user_setpoint/value
      scaler0_display_rate --> /entry/instrument/bluesky/streams/primary/scaler0_display_rate/value
      scaler0_time --> /entry/instrument/bluesky/streams/primary/scaler0_time/value
    instrument:NXinstrument
      bluesky:NXnote
        plan_name --> /entry/instrument/bluesky/metadata/plan_name
        uid --> /entry/instrument/bluesky/metadata/run_start_uid
        metadata:NXnote
          start.detectors = 'I0'
          start.hints = '{"dimensions": [[["pitch2"], "primary"]]}'
          start.motors = 'pitch2'
          start.num_intervals = 19
          start.num_points = 20
          start.plan_args = '{"args": ["EpicsMotor(prefix='25idDCM:AS:m6', name='pitc...'
          start.plan_name = 'rel_scan'
          start.plan_pattern = 'inner_product'
          start.plan_pattern_args = '{"args": ["EpicsMotor(prefix='25idDCM:AS:m6', name='pitc...'
          start.plan_pattern_module = 'bluesky.plan_patterns'
          start.plan_type = 'generator'
          start.purpose = 'alignment'
          start.scan_id = 1
          start.time = 1665065697.3635247
          start.uid = '7d1daf1d-60c7-4aa7-a668-d1cd97e5335f'
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
          summary.stream_names = 'primary'
          summary.timestamp = 1665065697.3635247
          summary.uid = '7d1daf1d-60c7-4aa7-a668-d1cd97e5335f'
        streams:NXnote
          baseline:NXnote
            aps_current:NXdata
              EPOCH:NX_FLOAT64[2] = [ ... ]
              time:NX_FLOAT64[2] = [ ... ]
              value:NX_FLOAT64[2] = [ ... ]
              value_end:NX_FLOAT64[] = [ ... ]
              value_start:NX_FLOAT64[] = [ ... ]
            aps_fill_number:NXdata
              EPOCH:NX_FLOAT64[2] = [ ... ]
              time:NX_FLOAT64[2] = [ ... ]
              value:NX_FLOAT64[2] = [ ... ]
              value_end:NX_FLOAT64[] = [ ... ]
              value_start:NX_FLOAT64[] = [ ... ]
            aps_global_feedback:NXdata
              EPOCH:NX_FLOAT64[2] = [ ... ]
              time:NX_FLOAT64[2] = [ ... ]
              value:NX_CHAR[3,3] = ["Off", "Off"]
              value_end:NX_CHAR = b'Off'
              value_start:NX_CHAR = b'Off'
            # many baseline groups omitted for brevity
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
                @units = 'A'
            energy:NXdata
              @axes = 'time'
              @signal = 'value'
              EPOCH = float64(100)
              time = float64(100)
                @units = 's'
              value = float64(100)
                @units = 'eV'
            ge_8element:NXdata
              value = float64(100x8x4096)
            ge_8element-element0-all_event:NXdata
              value = float64(100)
      detectors:NXnote
        I0_USAXS:NXdetector
          data --> /entry/instrument/bluesky/streams/primary/I0_USAXS
      monochromator:NXmonochromator
        energy --> /entry/instrument/bluesky/streams/baseline/monochromator_dcm_energy/value_start
        feedback_on --> /entry/instrument/bluesky/streams/baseline/monochromator_feedback_on/value_start
        mode --> /entry/instrument/bluesky/streams/baseline/monochromator_dcm_mode/value_start
        theta --> /entry/instrument/bluesky/streams/baseline/monochromator_dcm_theta/value_start
        wavelength --> /entry/instrument/bluesky/streams/baseline/monochromator_dcm_wavelength/value_start
        y_offset --> /entry/instrument/bluesky/streams/baseline/monochromator_dcm_y_offset/value_start
      positioners:NXnote
        m_stage_r:NXpositioner
          value --> /entry/instrument/bluesky/streams/primary/m_stage_r
      source:NXsource
        name:NX_CHAR = Bluesky framework
        probe:NX_CHAR = x-ray
        type:NX_CHAR = Synchrotron X-ray Source
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
    buff = bytes(await serialize_nexus(xafs_run, metadata=metadata, filter_for_access=None))
    buff = io.BytesIO(buff)
    with NexusIO(buff, mode="r") as fd:
        # Write data entry to the nexus file
        yield fd


@pytest.mark.asyncio
async def test_xafs_specification(nxfile):
    tree = nxfile.readfile().tree
    print(tree)
    assert tree == specification


@pytest.mark.asyncio
async def test_file_structure(nxfile):
    uid = "7d1daf1d-60c7-4aa7-a668-d1cd97e5335f"
    # Check the top-level entry
    assert nxfile.attrs["default"] == uid
    assert uid in nxfile.keys()
    entry = nxfile[uid]
    assert entry.attrs["NX_class"] == "NXentry"
