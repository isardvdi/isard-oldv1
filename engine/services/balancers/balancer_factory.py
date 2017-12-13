import inspect
from traceback import format_exc

from engine.services.balancers.central_manager import CentralManager
from engine.services.balancers.round_robin import RoundRobin
from engine.services.log import hypman_log as hmlog

BALANCER_TYPES = {'round_robin': RoundRobin, 'central_manager': CentralManager}


class BalancerFactory(object):
    @staticmethod
    def create(balancer_type, **kwargs):
        try:
            balancer = BALANCER_TYPES[balancer_type.lower()]
            args = inspect.getfullargspec(balancer.__init__).args
            params = {k:v for k,v in kwargs.items() if k in args}
            return balancer(**params)
        except Exception:
            hmlog.debug(inspect.getfullargspec(balancer.__init__).args)
            hmlog.error(format_exc())
            return None