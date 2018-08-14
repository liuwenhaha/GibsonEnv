from __future__ import print_function
import time, subprocess
import numpy as np
import sys, os
import gym
from tqdm import tqdm
from gibson.core.render.profiler import Profiler
from gibson.envs.husky_env import HuskyNavigateEnv
import itertools

class RandomAgent(object):
    """The world's simplest agent"""
    def __init__(self, action_space, is_discrete=False):
        self.action_space = action_space
        self.is_discrete = is_discrete
    def act(self, observation, reward=None):
        if self.is_discrete:
            action = np.random.randint(self.action_space.n)
        else:
            action = np.zeros(self.action_space.shape[0])
            if (np.random.random() < 0.2):
                action[np.random.choice(action.shape[0], 1)] = np.random.randint(-1, 2)
        return action

def get_config(fname):
    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'configs', 'fps', '{}.yaml'.format(fname))
    return config_file

def test_fps(fname, nframe=200):
    print("Benchmarking {}".format(fname))
    config = get_config(fname)
    env = HuskyNavigateEnv(config=config)
    #env = HuskyFetchEnv(human=args.human, timestep=1.0 / (4 * 22), frame_skip=4, is_discrete=True,  mode="DEPTH", use_filler=False, resolution = "NORMAL")
    obs = env.reset()
    agent = RandomAgent(env.action_space, is_discrete=True)
    assert (not obs is None)
    frame = 0
    score = 0
    restart_delay = 0
    obs = env.reset()
    ts = np.zeros((200,))
    assert (not obs is None)
    for frame in tqdm(range(nframe)):
        a = agent.act(obs)
        t = time.time()
        obs, r, done, meta = env.step(a)
        ts[frame] = time.time() - t
        score += r
    env.close()

    fps = "%.1f fps" % (1/np.mean(ts))
    print(np.mean(ts), fps)
    return fps 

res = 512
if __name__ == '__main__':
    agent = ["husky"]
    #res = [128, 256, 512]
    mode = ["smallfiller", "nonviz", "prefilled", "depth", "filled", "semantic", "normal"]
    #mode = ["smallfiller", "normal"]

    result = {}
    for a, m in itertools.product(agent, mode):
        if m not in result.keys():
            result[m] = {}
        result[m][res] = test_fps("benchmark_{}_{}_{}".format(a, m, res))
        time.sleep(1)
    print(result)
    import json
    with open("fps_{}.json".format(res), "w+") as f:
        json.dump(result, f, indent=2)