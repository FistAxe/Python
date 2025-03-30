def gen(n):
    print('gen consumed')
    if n == 1:
        yield 'halt'
        gen_builder(2)
        yield 'result'
    else:
        print('No')
        gen_builder(1)

def gen_builder(n):
    print('gen rebuilt')
    global g
    g = gen(n)

def gen_runner():
    print('\nrunning')
    global g
    try:
        print(next(g))
    except StopIteration:
        pass


gen_builder(1)
gen_runner()
gen_runner()
gen_runner()