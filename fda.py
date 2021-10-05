
def grad(x):
    g = [4 * x[0] + 3 * x[1] - 4, 3 * x[0] + 4 * x[1] + 2]
    print(g)
    return g

def update(x, grad):
    return [x[0] - 0.1 * grad[0], x[1] - 0.1 * grad[1]]

x = [1.0, 0.9]

for i in range(3):
    x = update(x, grad(x))
    print(f'x{i+1}:' f'[{round(x[0],2)}, {round(x[1],2)}]')