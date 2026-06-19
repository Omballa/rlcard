"""Train Kadi using DMC, DQN or NFSP agents (example)

This script is modeled after existing examples/run_rl.py and run_dmc.py.
It includes a `--debug` flag that prints sample trajectories and transition
details so you can verify inputs/outputs being fed to agents.
"""
import os
import argparse

import torch

import rlcard
from rlcard.utils import (
    get_device,
    set_seed,
    reorganize,
    Logger,
    tournament,
    plot_curve,
)


def train(args):
    device = get_device()
    set_seed(args.seed)

    # Make the Kadi environment
    env = rlcard.make('kadi', config={'seed': args.seed})

    if args.algorithm == 'dmc':
        # DMC trainer runs its own actor/learner processes; for debug, print
        # one sample episode then delegate to trainer unless --debug-only.
        from rlcard.agents.dmc_agent import DMCTrainer

        if args.debug:
            # Print one sample episode for verification
            trajectories, payoffs = env.run(is_training=True)
            print('Sample trajectories (first player):')
            for t in trajectories[0][:5]:
                print(t)
            if args.debug_only:
                return

        trainer = DMCTrainer(
            env,
            cuda=args.cuda,
            load_model=args.load_model,
            xpid=args.xpid,
            savedir=args.savedir,
            save_interval=args.save_interval,
            num_actor_devices=args.num_actor_devices,
            num_actors=args.num_actors,
            training_device=args.training_device,
        )

        trainer.start()
        return

    # For DQN and NFSP follow the typical RL training loop
    # Determine state length (support envs that expose `state_shape` or `state_space`)
    if hasattr(env, 'state_shape'):
        state_len = env.state_shape[0]
    elif hasattr(env, 'state_space') and isinstance(env.state_space, dict):
        state_len = env.state_space.get('obs_shape')[0]
    else:
        state_len = None

    if args.algorithm == 'dqn':
        from rlcard.agents import DQNAgent
        if args.load_checkpoint_path != "":
            agent = DQNAgent.from_checkpoint(checkpoint=torch.load(args.load_checkpoint_path))
        else:
            agent = DQNAgent(
                num_actions=env.num_actions,
                state_shape=state_len,
                mlp_layers=[64, 64],
                device=device,
                save_path=args.log_dir,
                save_every=args.save_every,
            )

    elif args.algorithm == 'nfsp':
        from rlcard.agents import NFSPAgent
        if args.load_checkpoint_path != "":
            agent = NFSPAgent.from_checkpoint(checkpoint=torch.load(args.load_checkpoint_path))
        else:
            agent = NFSPAgent(
                num_actions=env.num_actions,
                state_shape=state_len,
                hidden_layers_sizes=[64, 64],
                q_mlp_layers=[64, 64],
                device=device,
                save_path=args.log_dir,
                save_every=args.save_every,
            )
    else:
        raise ValueError('Unsupported algorithm: %s' % args.algorithm)

    # Use random agents as opponents
    from rlcard.agents import RandomAgent
    agents = [agent]
    for _ in range(1, env.num_players):
        agents.append(RandomAgent(num_actions=env.num_actions))
    env.set_agents(agents)

    # Training loop
    with Logger(args.log_dir) as logger:
        for episode in range(args.num_episodes):

            if args.algorithm == 'nfsp':
                agents[0].sample_episode_policy()

            trajectories, payoffs = env.run(is_training=True)

            # Show debug info if requested: sample transitions and shapes
            if args.debug and episode % max(1, args.debug_every) == 0:
                print('\nEpisode', episode, 'sample for player 0:')
                for i, ts in enumerate(trajectories[0][:5]):
                    # Trajectories from env.run may have different tuple lengths
                    # (pre-reorganize). Print structure safely for inspection.
                    if not isinstance(ts, (list, tuple)):
                        print('  Transition', i, 'value=', ts)
                        continue
                    if len(ts) >= 5:
                        try:
                            s = ts[0]
                            a = ts[1]
                            r = ts[2]
                            ns = ts[3]
                            done = ts[4]
                            print('  Transition', i, 'obs.shape=', s.get('obs').shape if isinstance(s, dict) and 'obs' in s else None,
                                  'legal=', list(s.get('legal_actions', {}).keys()) if isinstance(s, dict) else None,
                                  'action=', a,
                                  'reward=', r,
                                  'next_obs_shape=', ns.get('obs').shape if isinstance(ns, dict) and 'obs' in ns else None,
                                  'done=', done)
                        except Exception:
                            print('  Transition', i, 'contents=', ts)
                    else:
                        print('  Transition', i, 'contents=', ts)

            # Reorganize and feed transitions
            trajectories = reorganize(trajectories, payoffs)

            # Feed first player's transitions into agent
            for ts in trajectories[0]:
                agent.feed(ts)

            # Periodic evaluation
            if episode % args.evaluate_every == 0:
                perf = tournament(env, args.num_eval_games)[0]
                logger.log_performance(episode, perf)
                print('Episode', episode, 'evaluation perf:', perf)

        # Save model
        save_path = os.path.join(args.log_dir, 'model.pth')
        torch.save(agent, save_path)
        print('Model saved in', save_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Train Kadi with DMC/DQN/NFSP")
    parser.add_argument('--algorithm', type=str, default='dqn', choices=['dqn', 'nfsp', 'dmc'])
    parser.add_argument('--cuda', type=str, default='')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--num_episodes', type=int, default=5000)
    parser.add_argument('--num_eval_games', type=int, default=2000)
    parser.add_argument('--evaluate_every', type=int, default=100)
    parser.add_argument('--log_dir', type=str, default='experiments/kadi_result/')
    parser.add_argument('--load_checkpoint_path', type=str, default='')
    parser.add_argument('--save_every', type=int, default=-1)

    # DMC-specific args
    parser.add_argument('--load_model', action='store_true')
    parser.add_argument('--xpid', default='kadi', help='Experiment id for DMC')
    parser.add_argument('--savedir', default='experiments/dmc_result')
    parser.add_argument('--save_interval', default=30, type=int)
    parser.add_argument('--num_actor_devices', default=1, type=int)
    parser.add_argument('--num_actors', default=5, type=int)
    parser.add_argument('--training_device', default='0', type=str)

    # Debugging helpers
    parser.add_argument('--debug', action='store_true', help='Print sample transitions for verification')
    parser.add_argument('--debug-only', action='store_true', help='When used with --debug and dmc, only print a sample and exit')
    parser.add_argument('--debug_every', type=int, default=100, help='How often to print debug episode')

    args = parser.parse_args()
    os.environ['CUDA_VISIBLE_DEVICES'] = args.cuda
    train(args)
