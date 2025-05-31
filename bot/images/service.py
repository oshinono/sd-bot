import json
import uuid
from loguru import logger
from config import settings
from runware.types import IImageInference, IImage
import websockets
from runware import Runware

class ImgToTxtService:
    ws_url = 'wss://ws-api.runware.ai/v1'
    client = Runware(api_key=settings.rw_api_key)

    @classmethod
    async def _auth(cls, ws: websockets.WebSocketClientProtocol) -> str:
        auth_req = [{'taskType': 'authentication', 'apiKey': settings.rw_api_key}]
        await ws.send(json.dumps(auth_req))
        response = await ws.recv()
        return json.loads(response)

    @classmethod
    async def generate_ws(cls, data: IImageInference) -> list[IImage]:
        async with websockets.connect(cls.ws_url) as ws:
            auth_res = await cls._auth(ws)
            if not auth_res.get('connectionSessionUUID'):
                raise Exception('Не удалось авторизоваться: ' + '; '.join(auth_res.get('errors', [])))

            
            data_to_send = {
                'taskType': 'imageInference',
                'taskID': uuid.uuid4().hex,
                **data
            }

            await ws.send(json.dumps(data_to_send))
            response = await ws.recv()
            imgs = json.loads(response)
            return [IImage(**img) for img in imgs]
    
    @classmethod
    async def generate(cls, data: IImageInference) -> list[IImage] | None:
        await cls.client.connect()
        return await cls.client.imageInference(data)
