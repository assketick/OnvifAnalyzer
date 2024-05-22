import logging
from collections import OrderedDict
from zeep.helpers import serialize_object

logger = logging.getLogger("Imaging")

FUNCTIONS = {
    "GetOptions": "_get_options",
    "GetStatus": "_get_status",
    "GetPresets": "_get_presets",
    "GetCurrentPreset": "_get_current_preset",
    "SetCurrentPreset": "_set_current_preset",
    "GetImagingSettings": "_get_imaging_settings",
    "SetImagingSettings": "_set_imaging_settings",
    "GetMoveOptions": "_get_move_options",
    "Move": "_move",
    "Stop": "_stop",
}


class Imaging:

    def __init__(self, device):
        self.device = device

    async def _get_services(self):
        self.imaging_service = await self.device.create_imaging_service()
        self.media_service = await self.device.create_media_service()
        profiles = await self.media_service.GetProfiles()
        self.video_source_token = profiles[0].VideoSourceConfiguration.SourceToken

    async def run(self):
        await self._get_services()
        result = {}
        for function_name, func in FUNCTIONS.items():
            response = await getattr(self, func)(function_name)
            result = OrderedDict(result, **response)
        result = {"Imaging": result}
        return result

    async def _camera_call(self, service, function_name, params=None):
        try:
            if not params:
                response = await getattr(service, function_name)()
            else:
                response = await getattr(service, function_name)(params)
            response = serialize_object(response)
        except Exception as e:
            logger.warning(f"{function_name} - {e}")
            return "Не поддерживается"
        return response

    async def _get_imaging_settings(self, function_name):
        response = await self._camera_call(self.imaging_service, function_name, self.video_source_token)
        response.pop("Extension")
        self.device_brightness = response.get("Brightness")
        result = ""
        for field, value in response.items():
            if value and isinstance(value, dict):
                s = f"{field}:\n"
                for key, val in value.items():
                    if val:
                        s += f"\t{key} - {val}\n"
                result += s
            elif value and value != "None":
                result += f"{field}: {value}\n"
        result = result.rstrip()
        return {function_name: result}

    async def _get_move_options(self, function_name):
        response = await self._camera_call(self.imaging_service, function_name, self.video_source_token)
        result = ""
        for key, val in response.items():
            if val and key != "Continuous":
                result += f"{key} - {val}\n"
        result += f"Continuous Min Speed: {response.get('Continuous', {}).get('Speed', {}).get('Min')}\n"
        result += f"Continuous Max Speed: {response.get('Continuous', {}).get('Speed', {}).get('Max')}"
        return {function_name: result}

    async def _get_options(self, function_name):
        response = await self._camera_call(self.imaging_service, function_name, self.video_source_token)
        logger.info(response)
        response.pop("Extension")
        result = ""
        for field, value in response.items():
            if value and isinstance(value, dict):
                s = f"{field}:\n"
                for key, val in value.items():
                    if val and isinstance(val, list):
                        s += f"\t{key} - " + " or ".join(val) + "\n"
                    elif val and isinstance(val, dict):
                        s += f"\t{key}:\n"
                        for k, v in val.items():
                            s += f"\t\t{k} - {v}\n"
                    elif val or val == 0:
                        s += f"\t{key} - {val}\n"
                result += s
            elif value and isinstance(value, list):
                s = f"{field} {' or '.join(value)}\n"
                result += s
            elif value and value != 0:
                result += f"{field} - {value}\n"
        return {function_name: result.rstrip()}

    async def _get_presets(self, function_name):
        response = await self._camera_call(self.imaging_service, function_name, self.video_source_token)
        return {function_name: response}

    async def _get_status(self, function_name):
        response = await self._camera_call(self.imaging_service, function_name, self.video_source_token)
        response.pop("Extension")
        result = ""
        for field, value in response.items():
            if value and isinstance(value, dict):
                result += f"{field}:\n"
                for key, val in value.items():
                    if val:
                        result += f"\t{key} - {val}\n"
        return {function_name: result.rstrip()}

    async def _set_current_preset(self, function_name):
        response = await self._camera_call(self.imaging_service, function_name, self.video_source_token)
        return {function_name: response}

    async def _set_imaging_settings(self, function_name):
        imaging_type = self.imaging_service.create_type('SetImagingSettings')
        imaging_type.VideoSourceToken = self.video_source_token
        imaging_type.ImagingSettings = {"Brightness": 10}
        response = await self._camera_call(self.imaging_service, function_name, imaging_type)
        if not response:
            response = "Поддерживается"
        return {function_name: response}

    async def _get_current_preset(self, function_name):
        params = {
            "VideoSourceToken": self.video_source_token
        }
        response = await self._camera_call(self.imaging_service, function_name, params)
        if not response:
            return {function_name: response}
        return {function_name: response}

    async def _move(self, function_name):
        params = {
            "VideoSourceToken": self.video_source_token,
            "Focus": {}
        }
        focus_move_options = {
            "Absolute": {
                "Position": 0.5,
                "Speed": 0.3,
            },
            "Relative": {
                "Distance": 0.3,
                "Speed": 0.3,
            },
            "Continuous": {
                "Speed": 0.3,
            }
        }
        result = ""
        for key, val in focus_move_options.items():
            params["Focus"] = {key: val}
            response = await self._camera_call(self.imaging_service, function_name, params)
            result += f"{key} - Поддерживается\n" if not response else f"{key} - {response}\n"
        return {function_name: result.rstrip()}

    async def _stop(self, function_name):
        params = {
            "VideoSourceToken": self.video_source_token
        }
        response = await self._camera_call(self.imaging_service, function_name, params)
        if not response:
            return {function_name: "Поддерживается"}
        return {function_name: response}
