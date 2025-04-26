from redis.asyncio import Redis
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json
from app import config
import logging
import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StateRepository(ABC):
    @abstractmethod
    async def save_workflow_state(self, workflow_id: str, state: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_all_workflow_states(self) -> List[Dict[str, Any]]:
        pass


class InMemoryStateRepository(StateRepository):
    def __init__(self):
        self.states = {}

    async def save_workflow_state(self, workflow_id: str, state: Dict[str, Any]) -> None:
        self.states[workflow_id] = state

    async def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        return self.states.get(workflow_id)

    async def get_all_workflow_states(self) -> List[Dict[str, Any]]:
        return list(self.states.values())


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

    async def get_all_workflow_states(self) -> List[Dict[str, Any]]:
        try:
            if not self.redis_client:
                print("Redis client not available, falling back to in-memory storage")
                in_memory = InMemoryStateRepository()
                return await in_memory.get_all_workflow_states()
            try:
                keys = await self.redis_client.keys("*")
                if not keys:
                    print("No workflow states found in Redis")
                    return []

                values = await self.redis_client.mget(keys)
                states = []
                for value in values:
                    if value:
                        states.append(json.loads(value))
                return states

            except redis.exceptions.ConnectionError as e:
                # Handle Redis connection errors by falling back to in-memory
                print(f"Redis connection failed: {e}")
                print("Falling back to in-memory storage")
                self.redis_client = None  # Mark client as unavailable
                in_memory = InMemoryStateRepository()
                return await in_memory.get_all_workflow_states()

        except Exception as e:
            print(f"Error in get_all_workflow_states: {e}")
            # Return empty list rather than propagating the error
            return []