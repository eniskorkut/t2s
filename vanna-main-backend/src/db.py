from prisma import Prisma

# Global Prisma Client instance
prisma = Prisma()

async def connect_db():
    """Connect to the database."""
    if not prisma.is_connected():
        await prisma.connect()

async def disconnect_db():
    """Disconnect from the database."""
    if prisma.is_connected():
        await prisma.disconnect()
