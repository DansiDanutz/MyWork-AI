"""
Release escrow for due orders.

Usage:
  python tools/release_escrow.py
"""

import asyncio

from database import async_session_maker
from services.escrow import release_due_escrow


async def main() -> None:
    async with async_session_maker() as session:
        updated = await release_due_escrow(session)
        await session.commit()
        print(f"Released escrow for {updated} orders.")


if __name__ == "__main__":
    asyncio.run(main())
