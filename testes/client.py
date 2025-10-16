import asyncio
from asyncua import Client

async def list_endpoints():
    url = "opc.tcp://localhost:4840/freeopcua/server/"  # Ajuste a URL conforme necessário
    async with Client(url) as client:
        endpoints = await client.connect_and_get_server_endpoints()
        for ep in endpoints:
            print(ep)

asyncio.run(list_endpoints())