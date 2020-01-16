===========================
|cyclotron-logo| Cyclotron
===========================

.. |cyclotron-logo| image:: docs/asset/cyclotron_logo.png

A functional and reactive framework for `RxPY <https://github.com/ReactiveX/RxPY/>`_.

.. image:: https://travis-ci.org/MainRo/cyclotron-py.svg?branch=master
    :target: https://travis-ci.org/MainRo/cyclotron-py

.. image:: https://badge.fury.io/py/cyclotron.svg
    :target: https://badge.fury.io/py/cyclotron

.. image:: https://readthedocs.org/projects/cyclotron-py/badge/?version=latest
    :target: https://cyclotron-py.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status



----------------------

With Cyclotron, you can structure your RxPY code as many reusable components.
Moreover it naturally encourages to separate pure code and side effects. So a
Cyclotron application is easier to test, maintain, and extend.

Here is the structure of a cyclotron application:

.. figure:: https://github.com/mainro/cyclotron-py/raw/master/docs/asset/cycle.png
    :width: 60%
    :align: center

How to use it
=============

The following example is an http echo server:

.. code:: python

    from collections import namedtuple

    from cyclotron import Component
    from cyclotron.asyncio.runner import run
    import cyclotron_aiohttp.httpd as httpd
    import rx
    import rx.operators as ops

    EchoSource = namedtuple('EchoSource', ['httpd'])
    EchoSink = namedtuple('EchoSink', ['httpd'])
    EchoDrivers = namedtuple('EchoDrivers', ['httpd'])

    def echo_server(source):
        init = rx.from_([
            httpd.Initialize(),
            httpd.AddRoute(methods=['GET'], path='/echo/{what}', id='echo'),
            httpd.StartServer(host='localhost', port=8080),
        ])

        echo = source.httpd.route.pipe(
            ops.filter(lambda i: i.id == 'echo'),
            ops.flat_map(lambda i: i.request),
            ops.map(lambda i: httpd.Response(
                context=i.context,
                data=i.match_info['what'].encode('utf-8')),
            )
        )

        control = rx.merge(init, echo)
        return EchoSink(httpd=httpd.Sink(control=control))


    def main():
        run(Component(call=echo_server, input=EchoSource),
            EchoDrivers(httpd=httpd.make_driver()))


    if __name__ == '__main__':
        main()

In this application, the echo_server function is a pure function, while the http
server is implemented as a driver. 

.. code::

    pip install cyclotron-aiohttp

you can then test it with an http client like curl:

.. code::

    $ curl http://localhost:8080/echo/hello
    hello
    

Install
========

Cyclotron is available on PyPi and can be installed with pip:

.. code:: console

    pip install cyclotron

This project is composed of several python packages. Install also the ones that
you use in your application:

====================================================================  =========================
Package                                                               Version
====================================================================  =========================
`cyclotron <https://github.com/mainro/cyclotron-py>`_                 |pypi-cyclotron|
`cyclotron-std <https://github.com/mainro/cyclotron-std>`_            |pypi-cyclotron-std|
`cyclotron-aiohttp <https://github.com/mainro/cyclotron-aiohttp>`_    |pypi-cyclotron-aiohttp|
====================================================================  =========================

.. |pypi-cyclotron| image:: https://badge.fury.io/py/cyclotron.svg
    :target: https://badge.fury.io/py/cyclotron

.. |pypi-cyclotron-aiohttp| image:: https://badge.fury.io/py/cyclotron-aiohttp.svg
    :target: https://badge.fury.io/py/cyclotron-aiohttp

.. |pypi-cyclotron-std| image:: https://badge.fury.io/py/cyclotron-std.svg
    :target: https://badge.fury.io/py/cyclotron-std



License
=========

This project is licensed under the MIT License - see the `License
<https://github.com/mainro/cyclotron-py/raw/master/LICENSE.txt>`_ file for
details