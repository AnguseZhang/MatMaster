import inspect
import os
from pathlib import Path

USE_PHOTON = False
USER_DIRECT_CONSUME = True

MATMASTER_DIR = os.path.dirname(
    os.path.abspath(os.path.realpath(inspect.getfile(inspect.currentframe())))
)
PARAMETERS_OUTPUT_DIR = Path(MATMASTER_DIR).parent.parent / 'parameters_output'
