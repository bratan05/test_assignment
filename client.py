import sys
import requests
import numpy as np
import gevent
import gevent.monkey
gevent.monkey.patch_socket()  # required to allow asynchronous requests
from itertools import cycle
from matplotlib import pyplot


def get_response(min_c_re=-2.25, min_c_im=-1.25, max_c_re=0.75, max_c_im=1.25, x=2000, y=2000, inf_n=1024, port=4994, host='localhost'):
    """
    Get parts of the Mandelbrot set defined by input arguments.
    c is a complex number varied between min and max values on a grid of size x*y
    min_c_re:   lower bound on real part of c
    min_c_im:   lower bound on imaginary part of c
    max_c_re:   upper bound on real part of c
    max_c_im:   upper bound on imaginary part of c
    x, y:       grid dimensions
    inf_n:      maximum number of iterations 
    port, host: server address
    """
    with requests.get(f'http://{host}:{port}/mandelbrot/{min_c_re:.10f}/{min_c_im:.10f}/{max_c_re:.10f}/{max_c_im:.10f}/{x}/{y}/{inf_n}') as response:
        data = response.json()
        result = np.array(data['data'])
        return(result)


def divide_work(servers, number_of_divisions=1, min_c_re=-2.25, min_c_im=-1.25, max_c_re=0.75, max_c_im=1.25, Nx=2000, Ny=2000, inf_n=1024):
    """
    Spreads the workload over a set of servers to produce parts of Mandelbrot set.
    See "get_response()" function for meaning of parameters.
    """
    # First, define the global grid
    c_re = np.linspace(min_c_re, max_c_re, Nx)
    c_im = np.linspace(min_c_im, max_c_im, Ny)
    # Second, split the global grid into subparts
    real_parts = np.array_split(c_re, number_of_divisions)
    imag_parts = np.array_split(c_im, number_of_divisions)
    # Prepare output figure
    pyplot.figure(figsize=[12, 12], dpi=120)
    # Create a cyclic buffer from a list of servers
    servers = cycle(servers)

    def work(re, im, part):
        """
        Helper function: gets a part of Mandelbrot set and plots it
        """
        server = next(servers)
        response = get_response(
            min_c_re=re[0],
            min_c_im=im[0],
            max_c_re=re[-1],
            max_c_im=im[-1],
            x=np.size(re),
            y=np.size(im),
            inf_n=1024,
            port=server['port'],
            host=server['netloc'])
        X, Y = np.meshgrid(im, re)
        pyplot.pcolormesh(X, Y, response, cmap='Greys_r', vmin=0, vmax=255, rasterized=True)
        print(f"Done working on part: {part}")
    # Spawn a pool of threads for asynchronous execution and run them
    threads = [gevent.spawn(work, re, im, (i, j)) for i, re in enumerate(real_parts) for j, im in enumerate(imag_parts)]
    gevent.joinall(threads)
    # Annotate and save the figure
    pyplot.xlabel('Real part')
    pyplot.ylabel('Imaginary part')
    pyplot.title('Mandelbrot set')
    pyplot.savefig("mandelbrot.png")


if __name__ == "__main__":
    min_c_re = float(sys.argv[1])
    min_c_im = float(sys.argv[2])
    max_c_re = float(sys.argv[3])
    max_c_im = float(sys.argv[4])
    inf_n = int(sys.argv[5])
    x = int(sys.argv[6])
    y = int(sys.argv[7])
    number_of_divisions = int(sys.argv[8])
    list_of_servers = sys.argv[9:]
    servers = []
    for server in list_of_servers:
        item = server.split(':')
        servers.append({'netloc': item[0], 'port': item[1]})
    divide_work(
        servers=servers,
        min_c_re=min_c_re,
        min_c_im=min_c_im,
        max_c_re=max_c_re,
        max_c_im=max_c_im,
        inf_n=inf_n,
        Nx=x, Ny=y,
        number_of_divisions=number_of_divisions
    )
