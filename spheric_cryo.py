import numpy as np
import networkx as nx
from objects import ThermalObject
from material import Material
from material_data import material_data


def make_spherical_model(G: nx.DiGraph, parameter):
    cos = np.cos(np.linspace(0, np.pi, parameter['slice'] + 1))
    sin = np.sin(np.linspace(0, np.pi, parameter['slice'] + 1))

    def name(i_node):
        return f'{i_node}' + parameter['suffix']

    material = Material(material_data[parameter['material']])
    n_slice = parameter['slice']

    for i_node in range(n_slice):
        G.add_node(name(i_node))
        weight = -2*np.pi*parameter['radius']**2
        weight *= (cos[i_node + 1] - cos[i_node])*parameter['thickness']
        weight *= parameter['density']
        G.nodes[name(i_node)]['obj'] = ThermalObject(material, weight, 300)

    for i_pre, i_post in zip(range(n_slice - 1), range(1, n_slice)):
        name_pre, name_post = name(i_pre), name(i_post)
        G.add_edge(name_pre, name_post)
        area = 2*np.pi*parameter['radius']*parameter['thickness']*sin[i_post]
        distance = 2*parameter['radius']/n_slice

        G.edges[name_pre, name_post]['tc'] =\
            lambda t: material.thermal_conductivity(t, fill=True, exact=True)\
            * area / distance

    return G
