import aiohttp


class AiServiceError(Exception):
    pass


class AiService:
    def __init__(self, api_url: str, api_key: str, model: str = "gpt-4o-mini"):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Ты пишешь маркетинговые тексты на русском."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=payload, timeout=60) as r:
                    data = await r.json()
                    if r.status >= 400:
                        raise AiServiceError(f"AI API error {r.status}: {data}")
        except aiohttp.ClientError as e:
            raise AiServiceError(f"Network error: {e}") from e

        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError):
            raise AiServiceError(f"Unexpected AI response format: {data}")
