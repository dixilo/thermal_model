#!/usr/bin/env python3
from objects import PTC


def calc_flow(graph, dt):
    q_flow = {node: 0 for node in graph.nodes}

    for edge in graph.edges:
        obj1 = graph.nodes[edge[0]]['obj']
        obj2 = graph.nodes[edge[1]]['obj']
        temp_low = min(obj1.temperature, obj2.temperature)
        delta_t = obj2.temperature - obj1.temperature
        q = graph.edges[edge]['tc'](temp_low)*delta_t*dt

        q_flow[edge[0]] += q
        q_flow[edge[1]] -= q

    return q_flow


def apply(graph, q_flow, t_low, exact=True):
    for node in graph.nodes:
        obj = graph.nodes[node]['obj']
        obj.put_heat(q_flow[node], min_temp=t_low, exact=exact)


def run_ptc(graph, dt, ptc: PTC, node_pt1, node_pt2):
    temp_1 = graph.nodes[node_pt1]['obj'].temperature
    temp_2 = graph.nodes[node_pt2]['obj'].temperature
    q_1 = ptc.get_w1(temp_1, temp_2)*dt
    q_2 = ptc.get_w2(temp_1, temp_2)*dt

    return q_1, q_2

