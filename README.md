# Introduction
This is a simple client-server implementation of Mandelbrot set rendering process. The process is parallelised over a set of servers (started using server.py --port=port), where client (client.py) is responsible for work sharing and aggregation. 

## Installation
I suggest using [pipenv tool](https://github.com/pypa/pipenv):

    $ pipenv install numpy matplotlib gevent numba flask requests 

## Usage
First, activate the virtual environment:

    $ pipenv shell

Second, start one or more servers and specify the port to listen:

    $ python server.py --port=4994 &
    $ python server.py --port=4995 &
    $ ...

Finally, start the client with appropriate arguments:

    $ python client.py min_c_re min_c_im max_c_re max_c_im max_n x y divisions list_of_servers
    
The client produces a PNG image "mandelbrot.png"

## Known limitations
Matplotlib is used to simplify the plotting process. There are two issues with this approach. First, matplotlib uses too much memory for pcolormesh function. Second, there is a visible boundary between image subparts when total number of points along x or y dimension is less than 2000. 