import aiohttp
from typing import Optional
import json
import config


class Translator:
    def __init__(self):
        self.endpoint = config.AZURE_ENDPOINT
        self.key = config.AZURE_KEY
        self.region = "eastus"

    async def translate(
        self, text: str, source_lang: str = "en", target_lang: str = "es"
    ) -> Optional[str]:
        if not text:
            return None

        url = f"{self.endpoint}/translate?api-version=3.0&from={source_lang}&to={target_lang}"

        headers = {
            "Ocp-Apim-Subscription-Key": self.key,
            "Ocp-Apim-Subscription-Region": self.region,
            "Content-Type": "application/json",
        }

        body = [{"text": text}]

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, headers=headers) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                return data[0]["translations"][0]["text"]

        return None
