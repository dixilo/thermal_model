import pandas as pd
import numpy as np
from scipy.interpolate import LinearNDInterpolator
from material import Material

TEMP_MAX = 500.


def make_curve(t1, t2, ext_t1=False):
    t1 = list(t1)
    t2 = list(t2)
    if ext_t1:
        t1_mod = [t1[0]] + t1 + [t1[-1]]
        t2_mod = [0.] + t2 + [TEMP_MAX]
    else:
        t1_mod = [0.] + t1 + [TEMP_MAX]
        t2_mod = [t2[0]] + t2 + [t2[-1]]

    return t1_mod, t2_mod


class LoadCurvePT:
    def __init__(self, path):
        self._df = pd.read_csv(path)
        coord = list(zip(self._df['T1'], self._df['T2']))
        self._load_1 = LinearNDInterpolator(coord, self._df['load_1'])
        self._load_2 = LinearNDInterpolator(coord, self._df['load_2'])

        self._l1_low = self._df['load_1'].min()
        self._l2_low = self._df['load_2'].min()
        self._l1_high = self._df['load_1'].max()
        self._l2_high = self._df['load_2'].max()

        self._tb_1_low = self._df[self._df['load_1'] == self._l1_low]
        self._tb_2_low = self._df[self._df['load_2'] == self._l2_low]
        self._tb_1_high = self._df[self._df['load_1'] == self._l1_high]
        self._tb_2_high = self._df[self._df['load_2'] == self._l2_high]

        self._t1_low = make_curve(self._tb_1_low['T1'],
                                  self._tb_1_low['T2'], True)
        self._t1_high = make_curve(self._tb_1_high['T1'],
                                   self._tb_1_high['T2'], True)
        self._t2_low = make_curve(self._tb_2_low['T1'],
                                  self._tb_2_low['T2'], False)
        self._t2_high = make_curve(self._tb_2_high['T1'],
                                   self._tb_2_high['T2'], False)

    def load_1(self, t1, t2):
        data = self._load_1(t1, t2)

        if np.isnan(data):
            if t1 < np.interp(t2, self._t1_low[1], self._t1_low[0]):
                return self._l1_low
            if t1 > np.interp(t2, self._t1_high[1], self._t1_high[0]):
                return self._l1_high
            if t2 < np.interp(t1, self._t2_low[0], self._t2_low[1]):
                return np.interp(t1, self._tb_2_low['T1'],
                                 self._tb_2_low['load_1'])
            if t2 > np.interp(t1, self._t2_high[0], self._t2_high[1]):
                return np.interp(t1, self._tb_2_high['T1'],
                                 self._tb_2_high['load_1'])

        return data

    def load_2(self, t1, t2):
        data = self._load_2(t1, t2)

        if np.isnan(data):
            if t2 < np.interp(t1, self._t2_low[0], self._t2_low[1]):
                return self._l2_low
            if t2 > np.interp(t1, self._t2_high[0], self._t2_high[1]):
                return self._l2_high
            if t1 < np.interp(t2, self._t1_low[1], self._t1_low[0]):
                return np.interp(t2, self._tb_1_low['T2'],
                                 self._tb_1_low['load_2'])
            if t1 > np.interp(t2, self._t1_high[1], self._t1_high[0]):
                return np.interp(t2, self._tb_1_high['T2'],
                                 self._tb_1_high['load_2'])

        return data


class ThermalObject:
    def __init__(self, material: Material, mass, temperature):
        self._material = material
        self._mass = mass
        self.temperature = temperature

    def put_heat(self, Q, min_temp=4, exact=True):
        delta_temp = Q/self._mass
        delta_temp /= self._material.specific_heat(self.temperature,
                                                   fill=True, exact=exact)
        if self.temperature + delta_temp < min_temp:
            self.temperature = min_temp
        elif self.temperature + delta_temp > 300:
            return
        else:
            self.temperature += delta_temp


class PTC:
    def __init__(self, load_curve: LoadCurvePT):
        self._lc = load_curve
        self.t1_min = self._lc._tb_1_low['T1'].min()
        self.t2_min = self._lc._tb_2_low['T2'].min()

    def get_w1(self, temp_1, temp_2):
        return -self._lc.load_1(temp_1, temp_2)

    def get_w2(self, temp_1, temp_2):
        return -self._lc.load_2(temp_1, temp_2)
