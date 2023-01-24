import argparse

parser = argparse.ArgumentParser(description='Add some integers.')
parser.add_argument('integers', metavar='N', type=int, nargs='+',
                    help='integer list')
parser.add_argument('--sum', action='store_const',
                    const=sum, default=max,
                    help='sum the integers (default: find the max)')
args = parser.parse_args()
print(args.sum(args.integers))
