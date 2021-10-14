from dataclasses import dataclass, field
import numpy as np
import random
from typing import List

from entity_gym.environment import Environment, Entity, SelectEntity, ActionSpace, ObsConfig, Observation, ActionMask, Action


@dataclass
class CherryPick(Environment):
    cherries: List[float] = field(default_factory=list)
    last_reward: float = 0.0
    step: int = 0

    @classmethod
    def entities(cls) -> List[Entity]:
        return [
            Entity(
                name="Cherry",
                features=["quality"],
            ),
            Entity(
                name="Player",
                features=[],
            ),
        ]

    @classmethod
    def action_space(cls) -> List[ActionSpace]:
        return [SelectEntity("Pick Cherry")]

    def reset(self, obs_config: ObsConfig) -> Observation:
        cherries = [np.random.normal() for _ in range(32)]
        # Normalize so that the sum of the top 16 is 1.0
        top_16 = sorted(cherries, reverse=True)[:16]
        sum_top_16 = sum(top_16)
        normalized_cherries = [c / sum_top_16 for c in cherries]
        self.cherries = normalized_cherries
        self.last_reward = 0.0
        return self.filter_obs(self.observe(), obs_config)

    def observe(self) -> Observation:
        """
        @dataclass
        class Observation:
            # Maps each entity type to an array with features for each entity of that type.
            entities: Sequence[Tuple[str, np.ndarray]]
            # Maps each entity index to an identifier for the entity.
            ids: Sequence[int]
            # Maps each action type to an action mask.
            actions: Sequence[Tuple[str, ActionMask]]
            reward: float
            done: bool
        """
        return Observation(
            entities=[
                ("Cherry", np.array(self.cherries).reshape(-1, 1)),
                ("Player", np.zeros([1, 0])),
            ],
            ids=np.arange(len(self.cherries) + 1),
            action_masks=[
                ("Pick Cherry", ActionMask(
                    actors=[len(self.cherries)],
                    mask=(np.arange(len(self.cherries) + 1) <
                          len(self.cherries)).astype(np.float32),
                ))
            ],
            reward=self.last_reward,
            done=self.step == 16,
        )

    def act(self, actions: Action, obs_config: ObsConfig) -> Observation:
        for action_name, action_choices in actions.chosen_actions.items():
            self.last_reward = self.cherries.pop(action_choices[0][1])
        self.step += 1
        return self.filter_obs(self.observe(), obs_config)
