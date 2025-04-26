import logging
from typing import Optional
from redis.asyncio import Redis
import redis
import asyncio

from app import config
from app.core.repository import StateRepository, RedisStateRepository, InMemoryStateRepository

logger = logging.getLogger(__name__)


class RepositoryFactory:
    _instance: Optional[StateRepository] = None

    @classmethod
    async def initialize(cls):
        if cls._instance is not None:
            return

        await cls.get_repository()

    @classmethod
    async def get_repository(cls) -> StateRepository:
        """
        Get a repository instance. Tries to connect to Redis first,
        falls back to in-memory if Redis is not available.

        Returns:
            StateRepository: A repository instance
        """
        if cls._instance is not None:
            return cls._instance
        try:
            logger.info("Attempting to connect to Redis...")
            redis_client = Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=config.REDIS_DB,
                password=config.REDIS_PASSWORD,
                decode_responses=True
            )

            try:
                await asyncio.wait_for(redis_client.ping(), timeout=2.0)
                logger.info("Successfully connected to Redis")
                cls._instance = RedisStateRepository(redis_client)
                logger.info("Using Redis state repository")
                return cls._instance
            except (asyncio.TimeoutError, redis.exceptions.ConnectionError):
                logger.warning("Redis test failed")
                # Make sure to close the client to avoid connection leaks
                await redis_client.close()
                raise redis.exceptions.ConnectionError("Redis connection test failed")

        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            logger.warning("Falling back to in-memory storage")

        logger.info("Initializing in-memory state repository")
        cls._instance = InMemoryStateRepository()
        return cls._instance