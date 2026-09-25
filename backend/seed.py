import asyncio, uuid, datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

engine = create_async_engine('postgresql+asyncpg://postgres:admin_password@postgres:5432/agenttwinops')
async_session = async_sessionmaker(engine)

async def seed():
    async with async_session() as s:
        sid = '86c12b4e-7faf-45f2-8488-16547b65a2a6'
        await s.execute(text(f"INSERT INTO infrastructure (id, service_name, service_type, status, host) VALUES ('{sid}', 'test', 'test', 'ACTIVE', 'localhost') ON CONFLICT DO NOTHING"))
        now = datetime.datetime.now(datetime.timezone.utc)
        for i in range(40):
            await s.execute(text(f"INSERT INTO metrics (id, service_id, cpu_usage, memory_usage, disk_usage, network_usage, latency, timestamp) VALUES ('{uuid.uuid4()}', '{sid}', 50, 50, 50, 50, 50, '{now - datetime.timedelta(minutes=i)}')"))
        await s.commit()

asyncio.run(seed())
