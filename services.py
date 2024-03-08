import os
from typing import List
from onvif import ONVIFCamera
from collections import OrderedDict


def to_dict(self, services) -> List:
    services_str = str(services).replace(
        "<", "'<"
    ).replace(
        ">", ">'"
    )
    return eval(services_str)

async def get_services():

    cam = ONVIFCamera(
        os.getenv('IP'),
        os.getenv('PORT'),
        os.getenv('USERNAME'),
        os.getenv('PASSWORD'),
        wsdl_dir=r'/Users/nikkey/Library/Caches/pypoetry/virtualenvs/onvif_analyzer-dPSGSVP_-py3.11/lib/python3.11/site-packages/onvif/wsdl',
    )
    await cam.update_xaddrs()
    device_service = await cam.get_capabilities()
    services = OrderedDict()
    for service in device_service['Device']:
        if service not in ('XAddr', '_attr_1', 'Extension'):
            capabilities = device_service['Device'][service] or {}
            now = {}
            for key, val in capabilities.items():
                if key not in ('Extension', '_attr_1', '_value_1'):
                    now[key] = val
            services['device'] = services.get('device', []) + [{service: now}]

    for xaddr in cam.xaddrs.keys():
        service = xaddr.split('/')[-2]
        service_object = await cam.create_onvif_service(service)
        capabilities = to_dict(await service_object.GetServiceCapabilities())
        caps = {}
        for key, val in capabilities.items():
            if (
                isinstance(val, dict) and len(val) > 0 
                or not isinstance(val, dict) and val is not None
            ):
                caps[key] = val
        services[service] = caps

    return services