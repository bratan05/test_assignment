from flask import Flask, jsonify, abort, request, url_for
from gevent.pywsgi import WSGIServer
import numpy as np
from numba import jit
import argparse

# Workaround for negative numbers in URL
from werkzeug.routing import FloatConverter as BaseFloatConverter
class FloatConverter(BaseFloatConverter):
    regex = r'-?\d+(\.\d+)?'
# before routes are registered


app = Flask(__name__)
app.url_map.converters['float'] = FloatConverter

@app.route('/mandelbrot/<float:min_c_re>/<float:min_c_im>/<float:max_c_re>/<float:max_c_im>/<int:x>/<int:y>/<int:inf_n>', methods=['GET'])
def mandelbrot_api(min_c_re, min_c_im, max_c_re, max_c_im, x, y, inf_n):
    real = np.linspace(min_c_re, max_c_re, x)
    imag = np.linspace(min_c_im, max_c_im, y)
    return jsonify({
#        'real': real.tolist(),
#        'imag': imag.tolist(),
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
    #app.run(debug=True, threaded=True, port=4994)
