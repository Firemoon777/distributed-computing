import sys
import argparse


def main():
    # Parse cli args
    parser = argparse.ArgumentParser(description='Runs distributed system with P separated processes with shared stdout')
    parser.add_argument('-p', help='Count of concurrent process', type=int)
    parser.add_argument('--mutexl', help='Enable mutual exclusion with Lamport''s algorithm', action='store_true')
    args = parser.parse_args(sys.argv[1:])

    print(args.p)


if __name__ == '__main__':
    main()