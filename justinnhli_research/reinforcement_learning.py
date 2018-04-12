#!/usr/bin/env python3
"""Reinforcement learning agents and environments."""

from collections import defaultdict
from copy import copy
from random import random, choice


class Environment:
    """A reinforcement learning environment."""

    def get_state(self): # pylint: disable=redundant-returns-doc,missing-raises-doc
        """Get the current state.

        This is different from get_observation() in that the state includes
        otherwise hidden information that the agent may not have access to. As
        a rule, the state should be sufficient to completely reconstruct the
        environment. (Although this may not always be necessary, with a random
        seed for example.)

        Returns:
            State: The state, or None if at the end of an episode
        """
        raise NotImplementedError()

    def get_observation(self): # pylint: disable=redundant-returns-doc,missing-raises-doc
        """Get the current observation.

        See note on get_state() for the difference between the methods.

        Returns:
            State: The observation as a State, or None if the episode has ended
        """
        raise NotImplementedError()

    def get_actions(self): # pylint: disable=redundant-returns-doc,missing-raises-doc
        """Get the available actions.

        Returns:
            [Action]: A list of available actions.
        """
        raise NotImplementedError()

    def reset(self): # pylint: disable=redundant-returns-doc,missing-raises-doc
        """Reset the environment entirely.

        The result of calling this method should have the same effect as
        creating a new environment from scratch. Use new_episode() to reset the
        environment for a new episode.
        """
        raise NotImplementedError()

    def new_episode(self): # pylint: disable=redundant-returns-doc,missing-raises-doc
        """Reset the environment for a new episode.

        See note on reset() for the difference between the methods.
        """
        raise NotImplementedError()

    def react(self, action): # pylint: disable=redundant-returns-doc,missing-raises-doc
        """Update the environment to an agent action.

        Assumes the argument is one of the returned actions from get_actions().

        Arguments:
            action (Action): The action the agent took

        Returns:
            float: The reward for the agent for the previous action.
        """
        raise NotImplementedError()

    def visualize(self): # pylint: disable=redundant-returns-doc,missing-raises-doc
        """Create visualization of the environment.

        Returns:
            str: A visualization of the current state.
        """
        raise NotImplementedError()


class AttrDict:
    """A read-only dictionary that provides named-member access.

    This class acts as a read-only dictionary, but that also provides named-
    member access. Once initialized, the contents of the dictionary cannot
    be changed. In practice, could be used to create one-off objects that do
    not conform to any template (unlike collections.namedtuple).

    Examples:
        >>> ad = AttrDict(name="test", num=2)
        >>> ad['name']
        'test'
        >>> ad.name
        'test'
        >>> ad['num']
        2
        >>> ad.num
        2
    """

    def __init__(self, **kwargs):
        """Construct an AttrDict object.

        Arguments:
            **kwargs: Arbitrary key-value pairs
        """
        self._attributes_ = kwargs

    def __iter__(self):
        return self._attributes_.items().__iter__()

    def __getattr__(self, name):
        if name in self._attributes_:
            return self._attributes_[name]
        else:
            raise AttributeError('class {} has no attribute {}'.format(type(self).__name__, name))

    def __getitem__(self, key):
        return self._attributes_[key]

    def __hash__(self):
        return hash(tuple(sorted(self._attributes_.items())))

    def __eq__(self, other):
        # pylint: disable=protected-access
        return type(self) is type(other) and self._attributes_ == other._attributes_

    def __str__(self):
        return '{}({})'.format(
            type(self).__name__,
            ', '.join('{}={}'.format(*kv) for kv in sorted(self)),
        )

    def __repr__(self):
        return str(self)

    def as_dict(self):
        """Convert to dict.

        Returns:
            dict[str, any]: The internal dictionary.
        """
        return copy(self._attributes_)


class Action(AttrDict):
    """An action in a reinforcement learning environment."""

    def __init__(self, name, **kwargs):
        """Construct an Action object.

        Arguments:
            name (str): The name of the Action
            **kwargs: Arbitrary key-value pairs
        """
        super().__init__(**kwargs)
        self.name = name

    def __hash__(self):
        return hash(tuple([self.name, *sorted(self)]))

    def __str__(self):
        return 'Action("{}", {})'.format(
            self.name,
            ', '.join('{}={}'.format(*kv) for kv in sorted(self)),
        )


class State(AttrDict):
    """A state or observation in a reinforcement learning environment."""
    pass


class Agent:
    """A reinforcement learning agent."""

    def get_value(self, observation, action): # pylint: disable=redundant-returns-doc,missing-raises-doc
        """Get the Q value for an action at an observation.

        Arguments:
            observation (State): The observation
            action (Action): The action
        """
        raise NotImplementedError()

    def get_valued_actions(self, observation): # pylint: disable=redundant-returns-doc,missing-raises-doc
        """Get all actions with stored values at an observation.

        Arguments:
            observation (State): The observation.
        """
        raise NotImplementedError()

    def get_best_action(self, observation):
        """Get the action with the highest value at an observation.

        Arguments:
            observation (State): The observation.

        Returns:
            Action: The best action for the given observation.
        """
        actions = self.get_valued_actions(observation)
        if not actions:
            return None
        else:
            return max(actions, key=(lambda action: self.get_value(observation, action)))

    def get_best_value(self, observation):
        """Get the highest value at an observation.

        Arguments:
            observation (State): The observation.

        Returns:
            float: The value of the best action for the given observation.
        """
        return self.get_value(observation, self.get_best_action(observation))

    def act(self, observation, actions, reward=None): # pylint: disable=redundant-returns-doc,missing-raises-doc
        """Update the value function and decide on the next action.

        Arguments:
            observation (State): The observation of the environment.
            actions (list[Action]): List of available actions.
            reward (float): The reward from the previous action. If
                not provided, the observation will be treated as the first in a
                new episode.

        Returns:
            Action: The action the agent takes.
        """
        raise NotImplementedError()

    def force_act(self, observation, action, reward=None): # pylint: disable=redundant-returns-doc,missing-raises-doc
        """Update the value function and return a specific action.

        Arguments:
            observation (State): The observation of the environment.
            action (list[Action]): The action to return.
            reward (float): The reward from the previous action. If
                not provided, the observation will be treated as the first in a
                new episode.

        Returns:
            Action: The action the agent takes.
        """
        raise NotImplementedError()

    def print_value_function(self): # pylint: disable=redundant-returns-doc,missing-raises-doc
        """Print the value function."""
        raise NotImplementedError()


class TabularQLearningAgent(Agent):
    """A tabular Q-learning reinforcement learning agent."""

    def __init__(self, alpha, gamma):
        """Construct a tabular Q-learning agent.

        Arguments:
            alpha (float): The learning rate.
            gamma (float): The discount rate.
        """
        self.value_function = defaultdict((lambda: defaultdict(float)))
        self.learning_rate = alpha
        self.discount_rate = gamma
        self.prev_observation = None
        self.prev_action = None

    def get_value(self, observation, action): # noqa: D102
        if observation not in self.value_function:
            return 0
        return self.value_function[observation][action]

    def get_valued_actions(self, observation): # noqa: D102
        if observation not in self.value_function:
            return []
        return self.value_function[observation].keys()

    def act(self, observation, actions, reward=None): # noqa: D102
        best_action = self.get_best_action(observation)
        if best_action is None:
            best_action = choice(actions)
        return self.force_act(observation, best_action, reward)

    def force_act(self, observation, action, reward=None): # noqa: D102
        if self.prev_action is not None and reward is not None:
            self._observe_reward(observation, reward)
        self.prev_observation = observation
        if observation is None:
            self.prev_action = None
        else:
            self.prev_action = action
        return action

    def print_value_function(self): # noqa: D102
        for state, values in sorted(self.value_function.items(), key=(lambda kv: str(kv[0]))):
            print(state)
            for action, value in sorted(values.items(), key=(lambda kv: str(kv[0]))):
                print('    {}: {:.3f}'.format(action, value))

    def _observe_reward(self, observation, reward):
        """Update the value function with the reward.

        Arguments:
            observation (State): The current observation.
            reward (float): The reward from the previous action.
        """
        prev_value = self.get_value(self.prev_observation, self.prev_action)
        next_value = reward + self.discount_rate * self.get_best_value(observation)
        new_value = (1 - self.learning_rate) * prev_value + self.learning_rate * next_value
        self.value_function[self.prev_observation][self.prev_action] = new_value


def epsilon_greedy(cls, epsilon):
    """Decorate an Agent class to be epsilon-greedy.

    This decorator function takes a class (and a value of epsilon) and, on the
    fly, creates a sub-class which acts in an epsilon-greedy manner.
    """

    class EpsilonGreedyMetaAgent(cls):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.epsilon = epsilon

        def act(self, observation, actions, reward=None):
            if random() < self.epsilon:
                return super().force_act(observation, choice(actions), reward)
            else:
                return super().act(observation, actions, reward)

    return EpsilonGreedyMetaAgent


class GridWorld(Environment):

    def __init__(self, width, height, start, goal):
        self.width = width
        self.height = height
        self.start = list(start)
        self.goal = list(goal)
        self.row = start[0]
        self.col = start[1]

    def get_state(self):
        if [self.row, self.col] == self.goal:
            return None
        else:
            return State(row=self.row, col=self.col)

    def get_observation(self):
        return self.get_state()

    def get_actions(self):
        actions = []
        if self.row >= 0:
            actions.append(Action('up'))
        if self.row < self.height - 1:
            actions.append(Action('down'))
        if self.col >= 0:
            actions.append(Action('left'))
        if self.col < self.width - 1:
            actions.append(Action('right'))
        return actions

    def reset(self):
        self.new_episode()

    def new_episode(self):
        self.row = self.start[0]
        self.col = self.start[1]

    def react(self, action):
        assert action in self.get_actions()
        if [self.row, self.col] == self.goal:
            return 1
        else:
            if action.name == 'up':
                self.row = max(0, self.row - 1)
            elif action.name == 'down':
                self.row = min(self.height - 1, self.row + 1)
            elif action.name == 'left':
                self.col = max(0, self.col - 1)
            elif action.name == 'right':
                self.col = min(self.width - 1, self.col + 1)
            return -1


def gating_memory(cls, reward, num_memory_slots=1):

    class GatingMemoryMetaEnvironment(cls):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.reward = reward
            self.num_memory_slots = num_memory_slots
            self.memories = self.num_memory_slots * [None]

        def get_state(self):
            state = super().get_state()
            if state is None:
                return None
            state = state.as_dict()
            for key in list(state.keys()):
                if key.startswith('memory_'):
                    del state[key]
            memories = dict(zip(
                ['memory_{}'.format(i) for i in range(self.num_memory_slots)],
                self.memories,
            ))
            return AttrDict(**memories, **state)

        def get_observation(self):
            observation = super().get_observation()
            if observation is None:
                return None
            observation = observation.as_dict()
            for key in list(observation.keys()):
                if key.startswith('memory_'):
                    del observation[key]
            memories = dict(zip(
                ['memory_{}'.format(i) for i in range(self.num_memory_slots)],
                self.memories,
            ))
            return AttrDict(**memories, **observation)

        def get_actions(self):
            actions = super().get_actions()
            observations = super().get_observation()
            if observations is None:
                return actions
            for slot_num in range(self.num_memory_slots):
                for k, _ in observations:
                    if k == 'memory':
                        continue
                    actions.append(Action('gate', slot=slot_num, attribute=k))
            return actions

        def reset(self):
            super().reset()
            self.memories = self.num_memory_slots * [None]

        def new_episode(self):
            super().new_episode()
            self.memories = self.num_memory_slots * [None]

        def react(self, action):
            if action.name == 'gate':
                self.memories[action.slot] = getattr(super().get_observation(), action.attribute)
                return self.reward
            else:
                return super().react(action)

    return GatingMemoryMetaEnvironment


class TMaze(Environment):

    def __init__(self, length, hint_pos, hint_pos_2=None, redundant=False):
        assert 0 <= hint_pos <= length
        if hint_pos_2 is not None:
            assert 0 <= hint_pos_2 <= length
        if redundant:
            assert length >= 3
            assert hint_pos_2 is not None

        self.length = length
        self.hint_pos = hint_pos
        self.hint_pos_2 = hint_pos_2
        self.x = 0
        self.y = 0
        self.goal_x = choice([-1, 1])
        self.logical_connective = choice([-1, 1])
        self.direction = self.goal_x // self.logical_connective
        self.redundant = redundant
        self.redundant_connective = None
        self.redundant_direction = None
        if redundant:
            self.redundant_connective = -1 * self.logical_connective
            self.redundant_direction = -1 * self.direction

    def get_state(self):
        if self.y == self.length and self.x != 0:
            return None
        if self.hint_pos_2 is None:
            if self.y == self.hint_pos:
                return State(x=self.x, y=self.y, symbol=self.goal_x)
        else:
            if self.redundant:
                if self.y == self.hint_pos:
                    return State(x=self.x, y=self.y, symbol=self.logical_connective)
                elif self.y == self.hint_pos_2:
                    return State(x=self.x, y=self.y, symbol=self.direction)
                elif self.y == self.hint_pos - 2:
                    return State(x=self.x, y=self.y, symbol=self.redundant_connective)
                elif self.y == self.hint_pos_2 - 2:
                    return State(x=self.x, y=self.y, symbol=self.redundant_direction)
            else:
                if self.y == self.hint_pos:
                    return State(x=self.x, y=self.y, symbol=self.logical_connective)
                elif self.y == self.hint_pos_2:
                    return State(x=self.x, y=self.y, symbol=self.direction)
        return State(x=self.x, y=self.y, symbol=0)

    def get_observation(self):
        return self.get_state()

    def get_actions(self):
        actions = []
        if self.x == 0:
            if self.y < self.length:
                actions.append(Action('up'))
            elif self.y == self.length:
                actions.append(Action('left'))
                actions.append(Action('right'))
        else:
            actions.append(Action('halt'))
        return actions

    def reset(self):
        self.new_episode()

    def new_episode(self):
        self.x = 0
        self.y = 0
        self.goal_x = choice([-1, 1])
        self.logical_connective = choice([-1, 1])
        self.direction = self.goal_x // self.logical_connective
        self.redundant_connective = None
        self.redundant_direction = None
        if self.redundant:
            self.redundant_connective = -1 * self.logical_connective
            self.redundant_direction = -1 * self.direction

    def react(self, action):
        assert action in self.get_actions()
        if action.name == 'up':
            self.y += 1
        elif action.name == 'right':
            self.x += 1
        elif action.name == 'left':
            self.x -= 1
        if self.y == self.length:
            if self.x == self.goal_x:
                return 10
            elif self.x == -self.goal_x:
                return -10
            else:
                return -1
        elif action.name == 'gate':
            return -0.050
        else:
            return -1

    def visualize(self):
        lines = []
        for _ in range(self.length + 1):
            lines.append([' ', '_', ' '])
        lines[0][1 + self.goal_x] = '$'
        lines[0][1 - self.goal_x] = '#'
        lines[self.length - self.y][1] = '*'
        lines[self.length - self.hint_pos][1] = '!'
        if self.hint_pos_2 is not None:
            lines[self.length - self.hint_pos_2][1] = '?'
        return '\n'.join(''.join(line) for line in lines)


def run_interactive_episode(env, agent, num_episodes):
    for _ in range(num_episodes):
        env.new_episode()
        episodic_return = 0
        reward = None
        step = 0
        obs = env.get_observation()
        while obs is not None:
            print('step {}'.format(step))
            print(env.visualize())
            actions = env.get_actions()
            print('observation: {}'.format(obs))
            print('actions: {}'.format(actions))
            input()
            action = agent.act(obs, actions, reward)
            print('action: {}'.format(action))
            reward = env.react(action)
            obs = env.get_observation()
            episodic_return += reward
            print('reward: {}'.format(reward))
            step += 1
            print()
            print(10 * '-')
            print()
        print(env.visualize())
        agent.act(obs, env.get_actions(), reward)
        print('return: {}'.format(episodic_return))
        print(20 * '=')