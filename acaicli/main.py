from argparser import ArgumentLoader
from acaisdk.utils import utils


def main():
    utils.IS_CLI = True
    args, action = ArgumentLoader().parse()
    action.process()


if __name__ == "__main__":
    main()
