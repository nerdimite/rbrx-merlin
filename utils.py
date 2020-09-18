import parse

def parse_args(msg):
    # Get the argument pairs in a list
    args = list(map(lambda x: x.strip(), msg[len(msg.split()[0]):].split(',')))
    # Parse the arguments into a list of dicts
    args = list(map(lambda x: parse.parse('{col}={val}', x), args))

    return args