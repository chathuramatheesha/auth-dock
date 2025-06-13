import asyncio
from typing import Awaitable, Any


async def gather_with_exception_check(tasks: list[Awaitable[Any]]) -> list[Any]:
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            raise result

    return results
