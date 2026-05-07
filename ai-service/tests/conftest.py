import sys
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
AI_SERVICE_DIR = TESTS_DIR.parent

if str(AI_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(AI_SERVICE_DIR))
