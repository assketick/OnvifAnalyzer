import asyncio
import os
import pandas as pd
from typing import List
from onvif import ONVIFCamera
from collections import OrderedDict
from constants import (
    DEVICE,
    SERVICES
)
import sys
import logging
logger = logging.getLogger("Services")


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
        logger.warning(f"Connected!")


    async def get_services(self):
        await self.cam.update_xaddrs()
        device = await self._get_device_functions()
        services = await self._get_services()
        services["device"] = device.get("device")
        await self._write_excel(services)


    async def _get_device_functions(self):
        functions = SERVICES.get("device", [])
        service_object = await self.cam.create_devicemgmt_service()
        return await self._get_service_functions(functions, service_object, "device")


    async def _get_services(self):
        res = {}
        for xaddr in self.cam.xaddrs.keys():
            service = xaddr.split('/')[-2]
            # print(f'SERVICE - {service}')
            functions = SERVICES.get(service, [])
            # print(f'FUNCTIONS - {functions}\n\n')
            service_object = await self.cam.create_onvif_service(service)
            functions = await self._get_service_functions(functions, service_object, service)
            res[service] = functions
        return res
        

    async def _get_service_functions(self, functions, service_object, service_name):
        res = {}
        for function in functions:
            try:
                func = await getattr(service_object, function)()
                res[function] = str(func)
            except Exception as e:
                if 'service has no operation' in str(e):
                    res[function] = 'service has no operation'
                else:
                    # print(e)
                    ...
        return {service_name: res}
    

    async def _write_excel(self, services):
        with pd.ExcelWriter('output/res.xlsx') as writer:
            for service, functions in services.items():
                df = pd.DataFrame.from_dict(functions, orient='index')
                df.to_excel(writer, service)

    
if __name__ == "__main__":
    analyzer = OnvifAnalyzer("172.18.191.254", "80", "admin", "Supervisor")
    asyncio.run(analyzer.get_services())