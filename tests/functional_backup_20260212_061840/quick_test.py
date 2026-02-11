import asyncio

async def test():
    print("Async test works")
    return "OK"

result = asyncio.run(test())
print(f"Result: {result}")
