import sys
from django.apps import AppConfig

from .demo_dp_interface import DemoDPInterface

class EmpDemoDpInterfaceConfig(AppConfig):
    name = 'emp_demo_dp_interface'

    def ready(self):
        # Only if devl or prod server is started.
        if 'runserver' in sys.argv or "daphne" in sys.argv[0]:
            DemoDPInterface()
