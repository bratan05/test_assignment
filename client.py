import sys
import requests
import numpy as np
import gevent
import gevent.monkey
gevent.monkey.patch_socket()
from itertools import cycle
from matplotlib import pyplot


def get_response(min_c_re=-2.25, min_c_im=-1.25, max_c_re=0.75, max_c_im=1.25, x=2000, y=2000, inf_n=1024, port=4994, host='localhost'):
    with requests.get(f'http://{host}:{port}/mandelbrot/{min_c_re:.10f}/{min_c_im:.10f}/{max_c_re:.10f}/{max_c_im:.10f}/{x}/{y}/{inf_n}') as response:
        data = response.json()
        result = np.array(data['data'])
#        real = np.array(data['real'])
#        imag = np.array(data['imag'])
        return(result)


def plot():
    real, imag, result = get_response()
    X, Y = np.meshgrid(real, imag)
    pyplot.pcolormesh(X, Y, result, cmap='Greys_r')
    pyplot.xlabel('Real part')
    pyplot.ylabel('Imaginary part')
    pyplot.title('Mandelbrot set')
    pyplot.show()



def divide_work(servers, number_of_divisions=1, min_c_re=-2.25, min_c_im=-1.25, max_c_re=0.75, max_c_im=1.25, Nx=2000, Ny=2000, inf_n=1024):
    c_re = np.linspace(min_c_re, max_c_re, Nx)
    c_im = np.linspace(min_c_im, max_c_im, Ny)
    real_parts = np.array_split(c_re, number_of_divisions)
    imag_parts = np.array_split(c_im, number_of_divisions)
    pyplot.figure(figsize=[12, 12], dpi=120)
    print(servers)
    servers = cycle(servers)

    def helper(re, im, part):
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
    threads = [gevent.spawn(helper, re, im, (i, j)) for i, re in enumerate(real_parts) for j, im in enumerate(imag_parts)]
    gevent.joinall(threads)
    pyplot.xlabel('Real part')
    pyplot.ylabel('Imaginary part')
    pyplot.title('Mandelbrot set')
    pyplot.savefig("mandelbrot.png")


if __name__ == "__main__":
    # plot()

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
    # except Exception:
    #     print("Call using: python client.py min_c_re min_c_im max_c_re max_c_im inf_n x y number_of_divisions list_of_servers")
    #     print("Exception: ", Exception)
    #     sys.exit(-1)

    ###
    res = divide_work(number_of_divisions=number_of_divisions, Nx=x, Ny=y, servers=servers)
