Get Started
============

install cyclotron asyncio package:

.. code-block:: console

    $ pip3 install cyclotron_aiohttp


.. code-block:: python

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
            ops.filter(lambda i: i.id == 'echo')
            ops.flat_map(lambda i: i.request)
            ops.map(lambda i: httpd.Response(
                context=i.context,
                data=i.match_info['what'].encode('utf-8')))

        control = rx.merge(init, echo)
        return EchoSink(httpd=httpd.Sink(control=control))


    def main():
        run(Component(call=echo_server, input=EchoSource),
            EchoDrivers(httpd=httpd.make_driver()))


    if __name__ == '__main__':
        main()
