import datetime
from typing import IO
import io

import h5py
import pytest
import pytest_asyncio
from tiled.catalog.adapter import CatalogContainerAdapter
from nexusformat.nexus import nxopen, NXFile

from tiledspc.serialization.nexus import serialize_nexus, NexusFile


class NexusIO(NXFile):
    def __init__(self, bytesio: IO[bytes], mode: str='r', **kwargs):
        self.h5 = h5py
        self.name = ""
        self._file = None
        self._filename = "/dev/null"
        self._filedir = "/tmp"
        self._lock = None
        self._lockdir = None
        self._path = '/'
        self._root = None
        self._with_count = 0
        self.recursive = True

        self._file = self.h5.File(bytesio, mode, **kwargs)

        if mode == 'r':
            self._mode = 'r'
        else:
            self._mode = 'rw'

    def acquire_lock(self, timeout=None):
        pass

    def release_lock(self, timeout=None):
        pass

    def open(self, **kw):
        pass

    def close(self, **kw):
        pass


specification = """
root:NXroot
  @default = "7d1daf1d-60c7-4aa7-a668-d1cd97e5335f"
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
          APSTOOLS_VERSION:NX_CHAR = b'1.1.0'
          BLUESKY_VERSION:NX_CHAR = b'1.5.2'
          EPICS_CA_MAX_ARRAY_BYTES:NX_CHAR = b'1280000'
          EPICS_HOST_ARCH:NX_CHAR = b'linux-x86_64'
          OPHYD_VERSION:NX_CHAR = b'1.3.3'
          beamline_id:NX_CHAR = b'APS USAXS 9-ID-C'
          datetime:NX_CHAR = b'2019-05-02 17:45:33.904824'
          detectors:NX_CHAR = b'- I0_USAXS\n'
          hints:NX_CHAR = b'dimensions:\n- - - m_stage_r\n  - primary\n'
          login_id:NX_CHAR = b'usaxs@usaxscontrol.xray.aps.anl.gov'
          motors:NX_CHAR = b'- m_stage_r\n'
          pid:NX_INT64[] = [ ... ]
          plan_name:NX_CHAR = b'tune_mr'
          plan_type:NX_CHAR = b'generator'
          proposal_id:NX_CHAR = b'testing Bluesky installation'
          purpose:NX_CHAR = b'tuner'
          run_start_uid:NX_CHAR = 2ffe4d87-9f0c-464a-9d14-213ec71afaf7
          tune_md:NX_CHAR = b"initial_position: 8.824977\ntime_iso8601: '2019-05-02 17:45:33.923544'\nwidth: -0.004\n"
          tune_parameters:NX_CHAR = b'initial_position: 8.824977\nnum: 31\npeak_choice: com\nwidth: -0.004\nx_axis: m_stage_r\ny_axis: I0_USAXS\n'
          uid --> /entry/instrument/bluesky/run_start_uid
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
            I0_USAXS:NXdata
              EPOCH:NX_FLOAT64[31] = [ ... ]
              time:NX_FLOAT64[31] = [ ... ]
              value:NX_FLOAT64[31] = [ ... ]
            m_stage_r:NXdata
              EPOCH:NX_FLOAT64[31] = [ ... ]
              time:NX_FLOAT64[31] = [ ... ]
              value:NX_FLOAT64[31] = [ ... ]
            m_stage_r_soft_limit_hi:NXdata
              EPOCH:NX_FLOAT64[31] = [ ... ]
              time:NX_FLOAT64[31] = [ ... ]
              value:NX_FLOAT64[31] = [ ... ]
            m_stage_r_soft_limit_lo:NXdata
              EPOCH:NX_FLOAT64[31] = [ ... ]
              time:NX_FLOAT64[31] = [ ... ]
              value:NX_FLOAT64[31] = [ ... ]
            m_stage_r_user_setpoint:NXdata
              EPOCH:NX_FLOAT64[31] = [ ... ]
              time:NX_FLOAT64[31] = [ ... ]
              value:NX_FLOAT64[31] = [ ... ]
            scaler0_display_rate:NXdata
              EPOCH:NX_FLOAT64[31] = [ ... ]
              time:NX_FLOAT64[31] = [ ... ]
              value:NX_FLOAT64[31] = [ ... ]
            scaler0_time:NXdata
              EPOCH:NX_FLOAT64[31] = [ ... ]
              time:NX_FLOAT64[31] = [ ... ]
              value:NX_FLOAT64[31] = [ ... ]
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
    assert entry.attrs["default"] == "primary"
    # Check the default data group
    assert "primary" in entry.keys()
    primary = entry["primary"]
    assert primary.attrs["NX_class"] == "NXdata"
    # assert primary.attrs["signal"] == ""
    # assert primary.attrs["axes"] == "energy"
    # Check some of the run columns
    assert "energy" in primary.keys()
    assert primary["energy"].shape == (100,)
    assert "It-net_current" in primary.keys()
    assert "I0-net_current" in primary.keys()
    assert primary["energy"].attrs["NX_class"] == "NXdata"
    # assert False, primary['energy_energy']
