from redis.asyncio import Redis
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json
import logging

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
    _states: Dict[str, Dict[str, Any]] = {}

    def __init__(self):
        logger.info("Initializing InMemoryStateRepository")

    async def save_workflow_state(self, workflow_id: str, state: Dict[str, Any]) -> None:
        logger.debug(f"Saving workflow state: {workflow_id}")
        self._states[workflow_id] = state

    async def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        logger.debug(f"Getting workflow state: {workflow_id}")
        return self._states.get(workflow_id)

    async def get_all_workflow_states(self) -> List[Dict[str, Any]]:
        logger.debug(f"Getting all workflow states, count: {len(self._states)}")
        return list(self._states.values())


class RedisStateRepository(StateRepository):
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        logger.info("Initialized RedisStateRepository")

    async def save_workflow_state(self, workflow_id: str, state: Dict[str, Any]) -> None:
        try:
            logger.debug(f"Saving workflow state to Redis: {workflow_id}")
            state_json = json.dumps(state)
            await self.redis_client.set(workflow_id, state_json)
        except Exception as e:
            logger.error(f"Error saving workflow state to Redis: {e}")
            raise

    async def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        try:
            logger.debug(f"Getting workflow state from Redis: {workflow_id}")
            state_json = await self.redis_client.get(workflow_id)

            if not state_json:
                return None

            return json.loads(state_json)
        except Exception as e:
            logger.error(f"Error getting workflow state from Redis: {e}")
            raise

    async def get_all_workflow_states(self) -> List[Dict[str, Any]]:
        try:
            logger.debug("Getting all workflow states from Redis")
            keys = await self.redis_client.keys("*")

            if not keys:
                logger.info("No workflow states found in Redis")
                return []

            values = await self.redis_client.mget(keys)
            states = []

            for value in values:
                if value:
                    states.append(json.loads(value))

            logger.debug(f"Retrieved {len(states)} workflow states from Redis")
            return states
        except Exception as e:
            logger.error(f"Error getting all workflow states from Redis: {e}")
            raise