from flask import Flask, jsonify, abort, request, url_for
from gevent.pywsgi import WSGIServer
import numpy as np
from numba import jit
import argparse

# Workaround for negative numbers in URL
from werkzeug.routing import FloatConverter as BaseFloatConverter
class FloatConverter(BaseFloatConverter):
    regex = r'-?\d+(\.\d+)?'


app = Flask(__name__)
app.url_map.converters['float'] = FloatConverter


@app.route('/mandelbrot/<float:min_c_re>/<float:min_c_im>/<float:max_c_re>/<float:max_c_im>/<int:x>/<int:y>/<int:inf_n>', methods=['GET'])
def mandelbrot_api(min_c_re, min_c_im, max_c_re, max_c_im, x, y, inf_n):
    """
    Defines API for the server. Input arguments are:
    c is a complex number varied between min and max values on a grid of size x*y
    min_c_re:   lower bound on real part of c
    min_c_im:   lower bound on imaginary part of c
    max_c_re:   upper bound on real part of c
    max_c_im:   upper bound on imaginary part of c
    x, y:       grid dimensions
    inf_n:      maximum number of iterations
    """
    real = np.linspace(min_c_re, max_c_re, x)
    imag = np.linspace(min_c_im, max_c_im, y)
    return jsonify({
        'data': mandelbrot_set(real, imag, inf_n).tolist()
    })


@jit
def mandelbrot(z, maxiter):
    c = z
    for n in range(maxiter):
        if abs(z) > 2:
            return n % 256
        z = z*z + c
    return maxiter % 256


@jit
def mandelbrot_set(real, imag, inf_n):
    result = np.zeros((np.size(real), np.size(imag)))
    for i, re in enumerate(real):
        for j, im in enumerate(imag):
            result[i, j] = mandelbrot(complex(re, im), inf_n)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="Port to listen", type=int)
    args = parser.parse_args()
    server = WSGIServer(('localhost', args.port), app)
    server.serve_forever()
