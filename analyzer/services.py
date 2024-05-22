import sys
import logging
import pandas as pd
from onvif import ONVIFCamera
from collections import OrderedDict

from onvif_services.device import Device
from onvif_services.ptz import PTZ
from onvif_services.imaging import Imaging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Services")

SERVICE_MAP = {
    "device": Device,
    "ptz": PTZ,
    "imaging": Imaging,
}

class OnvifAnalyzer:
    def __init__(self, ip, port, username, password, to_save) -> None:
        wsdl_path = [f'{path}/onvif/wsdl' for path in sys.path if 'site-packages' in path][0]
        self.device = ONVIFCamera(ip, port, username, password, wsdl_dir=wsdl_path)
        self.device_service = {}
        self.to_save = to_save

    async def analyze(self):
        await self.device.update_xaddrs()
        logger.info(f"Connected. Xaddrs updated.")

        self.device_service["device"] = await self.device.create_devicemgmt_service()
        self.services = await self._get_services()
        self.services = dict(self.device_service, **self.services)
        logger.info(f"Available services - {self.services}")

        result = await self._get_supported_functions()
        filename = await self._write_excel(result)
        return filename

    async def _get_services(self):
        services = {}
        for xaddr in self.device.xaddrs.keys():
            service = xaddr.split('/')[-2].lower()
            service_object = await self.device.create_onvif_service(service)
            services[service] = service_object
        return services

    async def _get_supported_functions(self):
        result = {}
        for service_name, service_obj in SERVICE_MAP.items():
            logger.info(f"\n\n\nService - {service_name}")
            custom_service_obj = SERVICE_MAP.get(service_name)
            if custom_service_obj:
                custom_service_obj = custom_service_obj(self.device)
                service_functions = await custom_service_obj.run()
                logger.info(f"Service result - {service_functions}")
                result = OrderedDict(result, **service_functions)

        return result

    async def _write_excel(self, services):
        logger.info(self.to_save)
        try:
            with pd.ExcelWriter(self.to_save) as writer:
                for service_name, functions in services.items():
                    df = pd.DataFrame.from_dict(functions, columns=["Результат анализа"], orient='index')
                    df.to_excel(excel_writer=writer, sheet_name=service_name)
        except Exception as e:
            logger.error(e)