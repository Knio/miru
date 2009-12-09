
# this is really garbage

_cache = {}

def load_particles(char *filename, int cols):
    #if not _cache.has_key(filename):
    #    _cache.clear()
    fh = open(filename)
    data = []
    #_raw = []
    for line in fh:
        next = line[:-1].split(',')
        #_raw.append((float(next[0]), float(next[1]), float(next[2]),
        #    float(next[3])))
        for n in next[:cols]:
            data.append(float(n))
    #_cache[filename] = _raw
    fh.close()
    return data

def load_v3f_c3f(char *filename):
    fh = open(filename)
    vertices = []
    colors = []
    for line in fh:
        next = line[:-1].split(',')
        for n in next[:3]:
            vertices.append(float(n))
        v = float(next[-1]) / 150
        colors.extend((v, v, 1.0))
    fh.close()
    return vertices, colors

