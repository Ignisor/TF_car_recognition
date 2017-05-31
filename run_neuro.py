import sys

from data.neuro_model import Neuro


if __name__ == '__main__':
    n = Neuro()
    mode = sys.argv[1]

    if mode == 'train':
        try:
            steps = int(sys.argv[2])
            n.train(steps)
        except IndexError:
            n.train()
    elif mode == 'run':
        n.is_car(sys.argv[2])


