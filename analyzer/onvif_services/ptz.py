import logging
from analyzer.utils import ask_user
from collections import OrderedDict
from zeep.helpers import serialize_object
logger = logging.getLogger("PTZ")

FUNCTIONS = {
    'GetStatus': "_get_status",
    'GetPresets': "_get_presets",
    'GetConfiguration': "_get_configuration",
    'AbsoluteMove': "_absolute_move",
    'ContinuousMove': "_continuous_move",
    'Stop': "_stop",
    'RelativeMove': "_relative_move",
    'SetHomePosition': "_set_home_position",
    'SetPreset': "_set_preset",
    'GotoHomePosition': "_goto_home_position",
}

class PTZ:
    name = "PTZ"

    def __init__(self, device):
        self.device = device

    async def _get_services(self):
        self.media_service = await self.device.create_media_service()
        self.ptz = await self.device.create_ptz_service()
    async def _get_profiles(self):
        profiles = await self.media_service.GetProfiles()
        profile = profiles[0]
        self.token = profile.token
        logger.warning(f"TOKEN - {self.token}")

    async def run(self):
        await self._get_services()
        await self._get_profiles()
        result = {}
        for function_name, func in FUNCTIONS.items():
            response = await getattr(self, func)(function_name)
            result = OrderedDict(result, **response)
        result = {"PTZ": result}
        return result

    async def _camera_call(self, function_name, params=None):
        try:
            if not params:
                response = await getattr(self.ptz, function_name)()
            else:
                response = await getattr(self.ptz, function_name)(params)
        except Exception as e:
            logger.warning(f"{function_name} - {e}")
            return "Не поддерживается"
        return response

    async def _get_presets(self, function_name):
        response = await self._camera_call(function_name, self.token)
        response = serialize_object(response)
        if response:
            return {function_name: f"Presets found - {len(response)}"}

    async def _get_status(self, function_name):
        response = await self._camera_call(function_name, self.token)
        response = serialize_object(response)
        if isinstance(response, dict):
            position_x = response.get("Position", {}).get("PanTilt", {}).get("x")
            position_y = response.get("Position", {}).get("PanTilt", {}).get("y")
            zoom = response.get("Position", {}).get("Zoom", {}).get("x")
            move_status_pantilt = response.get("MoveStatus", {}).get("PanTilt")
            move_status_zoom = response.get("MoveStatus", {}).get("Zoom")
            return {
                function_name: f"Position:\n\tx: {position_x}\n\ty: {position_y}\n"
                               f"Zoom: {zoom}\n"
                               f"MoveStatus:\n\tPanTilt: {move_status_pantilt}\n\tZoom: {move_status_zoom}"
            }
        return response

    async def _get_configuration(self, function_name):
        response = await self._camera_call(function_name, self.token)
        response = serialize_object(response)
        if isinstance(response, dict):
            response.pop("_attr_1")
            result = ""
            for key, val in response.items():
                if val:
                    result += f"{key} - {val}"

            if not result:
                return {function_name: "Не настроено"}
            return result

        return {function_name: response}

    async def _absolute_move(self, function_name):
        message = f"Тестируем {self.__class__.name}:{function_name}. Проверьте, подвинулась ли камера?"
        params = {
            "ProfileToken": self.token,
            "Position": {
                'PanTilt': {'x': 0.7, 'y': 0.5},
                'Zoom': {'x': 0.5}
            },
            "Speed": {
                'PanTilt': {'x': 0.5, 'y': 0.5},
                'Zoom': {'x': 0.5}
            },
        }
        response = await self._camera_call(function_name, params)
        if not response:
            response = ask_user(message)
        return {function_name: response}

    async def _continuous_move(self, function_name):
        message = f"Тестируем {self.__class__.name}:{function_name}. Проверьте, начала ли двигаться камера"
        params = {
            "ProfileToken": self.token,
            "Velocity": {
                'PanTilt': {'x': 0.1, 'y': 0},
                'Zoom': {'x': 0.5}
            }
        }
        response = await self._camera_call(function_name, params)
        if not response:
            response = ask_user(message)
        return {function_name: response}

    async def _stop(self, function_name):
        message = f"Тестируем {self.__class__.name}:{function_name}. Проверьте, остановилась ли камера?"
        response = await self._camera_call(function_name, self.token)
        if not response:
            response = ask_user(message)
        return {function_name: response}

    async def _relative_move(self, function_name):
        message = f"Тестируем {self.__class__.name}:{function_name}. Проверьте, подвинулась ли камера?"
        params = {
            "ProfileToken": self.token,
            "Translation": {
                'PanTilt': {'x': 0.1, 'y': 0.1},
                'Zoom': {'x': 0.1}
            },
            "Speed": {
                'PanTilt': {'x': 0.5, 'y': 0.5},
                'Zoom': {'x': 0.5}
            },
        }
        response = await self._camera_call(function_name, params)
        if not response:
            response = ask_user(message)
        return {function_name: response}

    async def _set_preset(self, function_name):
        params = {
            "ProfileToken": self.token,
            "PresetName": "Preset1",
            "PresetToken": "1"
        }
        response = await self._camera_call(function_name, params)
        if response:
            return {function_name: "Поддерживается"}
        return {function_name: response}

    async def _set_home_position(self, function_name):
        params = {
            "ProfileToken": self.token
        }
        response = await self._camera_call(function_name, params)
        if not response:
            return {function_name: "Поддерживается"}
        return {function_name: response}

    async def _goto_home_position(self, function_name):
        message = f"Тестируем {self.__class__.name}:{function_name}. Вернулась ли камера в начальную позицию?"
        params = {
            "ProfileToken": self.token
        }
        response = await self._camera_call(function_name, params)
        if not response:
            response = ask_user(message)
        return {function_name: response}