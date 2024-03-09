import os
from typing import List
from onvif import ONVIFCamera
from collections import OrderedDict
import sys


def to_dict(services) -> List:
    services_str = str(services).replace(
        "<", "'<"
    ).replace(
        ">", ">'"
    )
    return eval(services_str)

class OnvifAnalyzer:
    def __init__(self, ip, port, username, password) -> None:
        wsdl_path = [f'{path}/onvif/wsdl' for path in sys.path if 'site-packages' in path][0]
        self.cam = ONVIFCamera(
            ip, 
            port, 
            username, 
            password,
            wsdl_dir=wsdl_path,
        )

    async def get_services(self):
        await self.cam.update_xaddrs()
        await self._get_services()
        await self._get_capabilities()
        return self.services


    async def _get_capabilities(self):
        device_service = await self.cam.get_capabilities()
        self.services = OrderedDict()
        for service in device_service['Device']:
            if service not in ('XAddr', '_attr_1', 'Extension'):
                capabilities = device_service['Device'][service] or {}
                now = {}
                for key, val in capabilities.items():
                    if key not in ('Extension', '_attr_1', '_value_1'):
                        now[key] = val
                self.services['device'] = self.services.get('device', []) + [{service: now}]
        return self.services

    async def _get_services(self):
        for xaddr in self.cam.xaddrs.keys():
            service = xaddr.split('/')[-2]
            service_object = await self.cam.create_onvif_service(service)
            capabilities = to_dict(await service_object.GetServiceCapabilities())
            caps = {}
            for key, val in capabilities.items():
                if (
                    isinstance(val, dict) and len(val) > 0 
                    or not isinstance(val, dict) and val is not None
                ):
                    caps[key] = val
            self.services[service] = caps

        return self.services