import json
import uuid
from loguru import logger
from config import settings
from runware.types import IImageInference, IImage
import websockets
from runware import Runware
from schemas import UserSettings

class ImgToTxtService:
    ws_url = 'wss://ws-api.runware.ai/v1'
    client = Runware(api_key=settings.rw_api_key)

    @classmethod
    async def _auth(cls, ws: websockets.WebSocketClientProtocol) -> bool:
        auth_req = [{'taskType': 'authentication', 'apiKey': settings.rw_api_key}]
        await ws.send(json.dumps(auth_req))
        response = await ws.recv()
        auth_res = json.loads(response)

        if not auth_res['data'][0].get('connectionSessionUUID'):
            raise Exception('Не удалось авторизоваться: ' + '; '.join(auth_res.get('errors', [])))
        return True

    @classmethod
    async def generate_ws(cls, data: UserSettings) -> list[IImage]:
        async with websockets.connect(cls.ws_url) as ws:
            await cls._auth(ws)
            dump = data.model_dump(exclude={'last_request_datetime'})
            dump['taskType'] = 'imageInference'
            dump['taskUUID'] = str(uuid.uuid4())

            await ws.send(json.dumps(dump))
            response = await ws.recv()
            json_res = json.loads(response)

            if json_res.get('errors'):
                raise Exception('Не удалось сгенерировать изображение: ' + json.dumps(json_res['errors'], indent=2))

            return [IImage(**img) for img in json_res['data'][0]]
    
    @classmethod
    async def generate(cls, data: IImageInference) -> list[IImage] | None:
        await cls.client.connect()
        return await cls.client.imageInference(data)
