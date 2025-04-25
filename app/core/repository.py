# app/core/repository.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
from redis.asyncio import Redis
import asyncio
from app import config


class StateRepository(ABC):
    @abstractmethod
    async def save_workflow_state(self, workflow_id: str, state: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        pass


class InMemoryStateRepository(StateRepository):
    def __init__(self):
        self.states = {}

    async def save_workflow_state(self, workflow_id: str, state: Dict[str, Any]) -> None:
        self.states[workflow_id] = state

    async def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        return self.states.get(workflow_id)


class RedisStateRepository(StateRepository):
    def __init__(self):
        try:
            self.redis_client = Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=config.REDIS_DB,
                password=config.REDIS_PASSWORD,
                decode_responses=True
            )
            self.redis_client.ping()
            print(f"Connected to Redis at {config.REDIS_HOST}:{config.REDIS_PORT}")
        except Exception as e:
            print(f"Warning: Redis connection failed: {e}")
            print("Falling back to in-memory storage")
            self.redis_client = None

    async def save_workflow_state(self, workflow_id: str, state: Dict[str, Any]) -> None:
        if not self.redis_client:
            # Fall back to in-memory if Redis is unavailable
            in_memory = InMemoryStateRepository()
            await in_memory.save_workflow_state(workflow_id, state)
            return

        state_json = json.dumps(state)
        key = workflow_id
        await self.redis_client.set(key, state_json)

    async def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        if not self.redis_client:
            # Fall back to in-memory if Redis is unavailable
            in_memory = InMemoryStateRepository()
            return await in_memory.get_workflow_state(workflow_id)

        key = workflow_id
        state_json = await self.redis_client.get(key)

        if not state_json:
            return None

        return json.loads(state_json)
