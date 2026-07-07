import asyncio
from app.agent import app

async def main():
    event = await app.root_agent.run_async("I had a $150 client dinner")
    print(event)

if __name__ == "__main__":
    asyncio.run(main())
