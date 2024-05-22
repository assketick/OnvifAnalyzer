import logging
from collections import OrderedDict
from zeep.helpers import serialize_object
logger = logging.getLogger("Device")

FUNCTIONS = {
    "GetHostname": "_get_host_name",
    "GetUsers": "_get_users",
    "GetDeviceInformation": "_get_device_information",
    "GetSystemDateAndTime": "_get_system_date_and_time",
}

class Device:

    def __init__(self, device):
        self.device = device

    async def _get_services(self):
        self.device_service = await self.device.create_devicemgmt_service()

    async def run(self):
        await self._get_services()
        capabilities = await self._get_capabilities()
        
        all_functions = {}
        for function in FUNCTIONS.values():
            response = await getattr(self, function)()
            all_functions = OrderedDict(all_functions, **response)
        all_functions = OrderedDict(all_functions, **capabilities)
        result = {"Device": all_functions}
        return result

    async def _camera_call(self, function_name, params=None):
        try:
            if not params:
                response = await getattr(self.device_service, function_name)()
            else:
                response = await getattr(self.device_service, function_name)(params)
        except Exception as e:
            logger.warning(e)
            return "Не поддерживается"
        
        if not response:
            return "Не поддерживается"
        return response
    
    async def _get_capabilities(self):
        response = await self._camera_call("GetServices", {"IncludeCapability": True})
        response_dict = serialize_object(response)
        result = {}
        for dct in response_dict[0].get("Capabilities").values():
            for functions in dct.values():
                if functions:
                    for key, val in functions.items():
                        if key == "_attr_1" and val:
                            for k, v in val.items():
                                if v:
                                    result[k] = "Yes" if isinstance(v, bool) or v == "true" else str(v)
                        elif val:
                            result[key] = "Yes" if isinstance(val, bool) or val == "true" else str(val)
        return result

    async def _get_host_name(self):
        name = "GetHostname"
        response = await self._camera_call(name)

        if response == "Не поддерживается":
            return {name: response}
        return {"GetHostname": response.Name}
    
    async def _get_device_information(self):
        name = "GetDeviceInformation"
        response = await self._camera_call(name)

        if response == "Не поддерживается":
            return {name: response}
        return {
            name: f"Model - {response.Model}\n"
                  f"SerialNumber - {response.SerialNumber}"
        }

    async def _get_system_date_and_time(self):
        name = "GetSystemDateAndTime"
        response = await self._camera_call(name)
        if response == "Не поддерживается":
            return {name: response}
        
        time = []
        for key in response.UTCDateTime.Time:
            time += [str(getattr(response.UTCDateTime.Time, key))]

        date = []
        for key in response.UTCDateTime.Date:
            date += [str(getattr(response.UTCDateTime.Date, key))]

        return {
            name: f"Timezone - {[t for t in response.TimeZone][0]}\n"
                  f"UTC Datetime - {':'.join(time)}, {':'.join(date)}"
        }

    async def _get_users(self):
        name = "GetUsers"
        response = await self._camera_call(name)
        return {   
            name: "\n".join([
                f"User - {dct.Username}, Level - {dct.UserLevel}"
                for dct in response
            ])
        }
