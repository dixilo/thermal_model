import pandas as pd
import numpy as np
import io


class Material:
    def __init__(self, txt):
        self._df = pd.read_csv(io.StringIO(txt), sep='\t',
                               names=['name',
                                      'thermal_conductivity',
                                      'specific_heat'])
        self._tc_cache = {}
        self._sh_cache = {}

    def thermal_conductivity(self, temp, fill=False, limit=4, exact=True):
        if not exact:
            if (fill, limit) not in self._tc_cache:
                t = np.arange(0, 330, 1)
                v = [self.thermal_conductivity(_t, fill=fill,
                                               limit=limit, exact=True)
                     for _t in t]
                self._tc_cache[(fill, limit)] =\
                    lambda temp: np.interp(temp, t, v)

            return self._tc_cache[(fill, limit)](temp)

        if fill:
            if temp < limit:
                val_l = self.thermal_conductivity(limit, fill=False)
                return np.interp(temp, [0, limit], [0, val_l])

        lt = np.log10(temp)
        power = [val*(lt**i) for i, val
                 in enumerate(self._df['thermal_conductivity'])]

        return np.power(10, sum(power))

    def specific_heat(self, temp, fill=False, limit=4, exact=True):
        if not exact:
            if (fill, limit) not in self._sh_cache:
                t = np.arange(0, 330, 1)
                v = [self.specific_heat(_t, fill=fill,
                                        limit=limit, exact=True)
                     for _t in t]
                self._sh_cache[(fill, limit)] =\
                    lambda temp: np.interp(temp, t, v)

            return self._sh_cache[(fill, limit)](temp)

        if fill:
            if temp < limit:
                val_l = self.specific_heat(limit, fill=False)
                return np.interp(temp, [0, limit], [0, val_l])

        lt = np.log10(temp)
        power = [val*(lt**i) for i, val
                 in enumerate(self._df['specific_heat'])]

        return np.power(10, sum(power))
