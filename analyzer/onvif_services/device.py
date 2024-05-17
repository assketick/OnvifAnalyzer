import sys
import logging
import asyncio
from onvif import ONVIFCamera
logger = logging.getLogger("Services")



class Device:

    def __init__(self, device):
        self.device = device

    async def run(self):
        response = await self.get_host_name()
        logging.warning(response)
        response = await self.get_device_information()
        logging.warning(response)
        response = await self.get_discovery_mode()
        logging.warning(response)
        response = await self.get_dns()
        logging.warning(response)
        response = await self.get_dot11_capabilities()
        logging.warning(response)
        # response = await self.get_dot11_status()
        # logging.warning(response)
        response = await self.get_dpa_adress()
        logging.warning(response)
        response = await self.get_dynamic_dns()
        logging.warning(response)
        # response = await self.get_endpoint_reference()
        # logging.warning(response)
        response = await self.get_ip_adress_filter()
        logging.warning(response)
        response = await self.get_network_default_gateway()
        logging.warning(response)
        response = await self.get_network_interfaces()
        logging.warning(response)
        response = await self.get_network_protocols()
        logging.warning(response)
        # response = await self.get_NTP()
        # logging.warning(response)
        response = await self.get_password_complexity_configuration()
        logging.warning(response)
        response = await self.get_password_complexity_options()
        logging.warning(response)
        response = await self.get_password_complexity_history_configuration()
        logging.warning(response)
        response = await self.get_remote_discovery_mode()
        logging.warning(response)
        response = await self.get_remote_user()
        logging.warning(response)
        response = await self.get_scopes()
        logging.warning(response)
        # response = await self.get_services()
        # logging.warning(response)
        response = await self.get_storage_configuration()
        logging.warning(response)
        response = await self.get_storage_configurations()
        logging.warning(response)
        response = await self.get_system_backup()
        logging.warning(response)
        response = await self.get_system_date_and_time()
        logging.warning(response)
        logging.warning(response)
        response = await self.get_system_log()
        logging.warning(response)
        response = await self.get_system_suport_information()
        logging.warning(response)
        # response = await self.get_system_uris()
        # logging.warning(response)
        response = await self.get_users()
        logging.warning(response)

    async def _camera_call(self, service_name, params=None):
        try:
            if not params:
                response = await getattr(self.device, service_name)()
            else:
                response = await getattr(self.device, service_name)(params)
        except Exception as e:
            logger.warning(e)
            return "Не поддерживается"
        
        if not response:
            return "Не поддерживается"
        return response

    async def get_host_name(self):
        name = "GetHostname"
        response = await self._camera_call(name)

        if response == "Не поддерживается":
            return {name: response}

        return {"GetHostname": response.Name}
    
    async def get_device_information(self):
        name = "GetDeviceInformation"
        response = await self._camera_call(name)

        if response == "Не поддерживается":
            return {name: response}
        return {
            name: {
                "Model": response.Model,
                "SerialNumber": response.SerialNumber,
            }
        }

    async def get_discovery_mode(self):
        name = "GetDiscoveryMode"
        response = await self._camera_call(name)
        return {name: response}

    async def get_dns(self):
        name = "GetDNS"
        response = await self._camera_call(name)

        if response == "Не поддерживается":
            return {name: response}
        return {
            name: {
                "FromDHCP": response.FromDHCP,
                "DNSFromDHCP": {
                    "IPv4Address": response.DNSFromDHCP[0].IPv4Address,
                    "IPv6Address": response.DNSFromDHCP[0].IPv6Address
                }
            }
        }
    
    async def get_dot11_capabilities(self):
        name = "GetDot11Capabilities"
        response = await self._camera_call(name)

        if response == "Не поддерживается":
            return {name: response}
        return {
            name: {
                key: getattr(response, key)
                for key in response
                if getattr(response, key) is not None
            }
        }
    
    # async def get_dot11_status(self):
    #     response = await getattr(self.device, "GetDot11Status")({"InterfaceToken":"TKIP"})
    #     if not response:
    #         return {"GetDot11Status": "Не поддерживается"}
    #     return {"GetDot11Status": response}
    
    async def get_dpa_adress(self):
        name = "GetDPAddresses"
        response = await self._camera_call(name)

        if response == "Не поддерживается":
            return {name: response}

        return {
            name: [
                {
                    key: getattr(dct, key)
                    for key in dct
                    if getattr(dct, key) is not None
                }
                for dct in response
            ]
        }
    
    async def get_dynamic_dns(self):
        name = "GetDynamicDNS"
        response = await self._camera_call(name)
        return {name: response}
    
    # async def get_endpoint_reference(self):
    #     response = await getattr(self.device, "GetEndpointReference")()
    #     if not response:
    #         return {"GetEndpointReference": "Не поддерживается"}
    #     return {"GetEndpointReference": response}

    async def get_ip_adress_filter(self):
        name = "GetIPAddressFilter"
        response = await self._camera_call(name)
        if response == "Не поддерживается":
            return {name: response}
        return {
            name: {
                key: getattr(response, key)
                for key in response
                if getattr(response, key) is not None
            }
        }
    
    async def get_network_default_gateway(self):
        name = "GetNetworkDefaultGateway"
        response = await self._camera_call(name)
        return {name: response}
    
    async def get_network_interfaces(self):
        name = "GetNetworkInterfaces"
        response = await self._camera_call(name)
        return {name: response}
    
    async def get_network_protocols(self):
        name = "GetNetworkProtocols"
        response = await self._camera_call(name)

        if response == "Не поддерживается":
            return {name: response}

        return {
            name: [
                {
                    key: getattr(dct, key)
                    for key in dct
                    if getattr(dct, key) is not None
                }
                for dct in response
            ]
        }
    
    # async def get_NTP(self):
    #     response = await getattr(self.device, "GetNTP")()
    #     if not response:
    #         return {"GetNTP": "Не поддерживается"}
    #     return {
    #         "GetNTP": {

    #         }
    #     }

    async def get_password_complexity_configuration(self):
        name = "GetPasswordComplexityConfiguration"
        response = await self._camera_call(name)
        return {name: response}
    
    async def get_password_complexity_options(self):
        name = "GetPasswordComplexityOptions"
        response = await self._camera_call(name)
        return {name: response}
    
    async def get_password_complexity_history_configuration(self):
        name = "GetPasswordHistoryConfiguration"
        response = await self._camera_call(name)
        return {name: response}
    
    async def get_remote_discovery_mode(self):
        name = "GetRemoteDiscoveryMode"
        response = await self._camera_call(name)
        return {name: response}
    
    async def get_remote_user(self):
        name = "GetRemoteUser"
        response = await self._camera_call(name)
        return {name: response}
    
    async def get_scopes(self):
        name = "GetScopes"
        response = await self._camera_call(name)
        return {name: response}

    async def get_services(self):
        name = "GetServices"
        response = await self._camera_call(name, {"IncludeCapability": True})
        return {name: response}
    
    async def get_storage_configuration(self):
        name = "GetStorageConfiguration"
        response = await self._camera_call(name)
        return {name: response}
    
    async def get_storage_configurations(self):
        name = "GetStorageConfigurations"
        response = await self._camera_call(name)
        return {name: response}

    async def get_system_backup(self):
        name = "GetSystemBackup"
        response = await self._camera_call(name)
        return {name: response}

    async def get_system_date_and_time(self):
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
            name: {
                "Timezone": response.TimeZone,
                "UTC Datetime": f"{':'.join(time)} {':'.join(date)}"
            }
        }
    
    async def get_system_log(self):
        name = "GetSystemLog"
        response = await self._camera_call(name, {"LogType": "System"})
        return {name: response.String}
    
    async def get_system_suport_information(self):
        name = "GetSystemSupportInformation"
        response = await self._camera_call(name)
        return {name: response.String}

    async def get_system_uris(self):
        name = "GetSystemUris"
        response = await self._camera_call(name)
        return {name: response}

    async def get_users(self):
        name = "GetUsers"
        response = await self._camera_call(name)
        return {   
            name: [
                {
                    "Username": dct.Username,
                    "UserLevel": dct.UserLevel,
                }
                for dct in response
            ]
        }
    

if __name__ == "__main__":
    wsdl_path = [f'{path}/onvif/wsdl' for path in sys.path if 'site-packages' in path][0]
    analyzer = ONVIFCamera(host="172.18.212.18", port="80", user="admin", passwd="Supervisor", wsdl_dir=wsdl_path)
    device_service = asyncio.run(analyzer.create_devicemgmt_service())
    device = Device(device_service)
    asyncio.run(device.run())