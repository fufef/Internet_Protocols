import json

filename = 'cache.json'


def get_cache():
    with open(filename, "r") as f:
        cache = json.load(f)
    return cache


def write_in_cache(data):
    cache = get_cache()
    cache[data[0]] = data[1]
    with open(filename, "w") as f:
        json.dump(cache, f, indent=4)


# def main():
#     data = ('exmpl', [['ehlo', 'hh'], ['df', 'fdf'], 'nigger'])
#     write_in_cache(data)
#
#     dt = get_cache()
#     print(dt)
#     print(type(dt))
#
#
# if __name__ == '__main__':
#     main()
