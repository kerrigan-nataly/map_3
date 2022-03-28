def set_map_params(toponym_longitude, toponym_lattitude, z=12, l='map'):
    return {
    "ll": ",".join([toponym_longitude, toponym_lattitude]),
    "z": z,
    "l": l}
