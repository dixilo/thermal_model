#!/usr/bin/env python3
'''Simulation of cooling process with spheric cryostat model.'''
import networkx as nx
import numpy as np
import pandas as pd

from spheric_cryo import make_spherical_model
from objects import PTC, LoadCurvePT
from calculator import run_ptc, calc_flow, apply

from argparse import ArgumentParser
from tqdm import tqdm
import yaml


def main():
    parser = ArgumentParser()
    parser.add_argument('yaml_path',
                        help='Path to the yaml configuration file.')
    parser.add_argument('ptc_path',
                        help='Path to the PTC load curve file.')
    parser.add_argument('out_path',
                        help='Path to the output file.')

    args = parser.parse_args()
    with open(args.yaml_path, 'r') as yml:
        config = yaml.safe_load(yml)

    G = nx.DiGraph()
    make_spherical_model(G, config['cryo_4K'])
    make_spherical_model(G, config['cryo_40K'])

    ptc = PTC(LoadCurvePT(args.ptc_path))

    time_series = [0.]
    temperatures = []
    temperatures.append([G.nodes[node]['obj'].temperature for node
                         in G.nodes])

    time_current = 0.
    dt_now = 20.

    for i in tqdm(range(200000)):
        q_flow = calc_flow(G, dt_now)
        q1_ptc, q2_ptc = run_ptc(G, dt_now, ptc, '0_40K', '0_4K')
        q_flow['0_40K'] += q1_ptc
        q_flow['0_4K'] += q2_ptc
        apply(G, q_flow, ptc.t2_min, exact=True)

        temperatures.append([G.nodes[node]['obj'].temperature for node
                             in G.nodes])
        time_current += dt_now
        time_series.append(time_current)

        if (q_flow['0_40K'] > 0) or (q_flow['0_4K'] > 0):
            dt_now /= 2

    df = pd.DataFrame(temperatures,
                      columns=list(G.nodes), index=time_series)
    df.to_csv(args.out_path)


if __name__ == '__main__':
    main()
