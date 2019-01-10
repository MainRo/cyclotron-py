Get Started
============

install cyclotron asyncio package:

.. code-block:: console

    $ pip3 install cyclotron-aio


.. code-block:: python

    from collections import namedtuple

    from cyclotron import Component
    from cyclotron_aio.runner import run
    import cyclotron_aio.httpd as httpd
    from rx import Observable

    EchoSource = namedtuple('EchoSource', ['httpd'])
    EchoSink = namedtuple('EchoSink', ['httpd'])
    EchoDrivers = namedtuple('EchoDrivers', ['httpd'])


    def echo_server(source):
        init = Observable.from_([
            httpd.Initialize(),
            httpd.AddRoute(methods=['GET'], path='/echo/{what}', id='echo'),
            httpd.StartServer(host='localhost', port=8080),
        ])

        echo = (
            source.httpd.route
            .filter(lambda i: i.id == 'echo')
            .flat_map(lambda i: i.request)
            .map(lambda i: httpd.Response(
                context=i.context,
                data=i.match_info['what'].encode('utf-8')))

        control = Observable.merge(init, echo)
        return EchoSink(httpd=httpd.Sink(control=control))


    def main():
        run(Component(call=echo_server, input=EchoSource),
            EchoDrivers(httpd=httpd.make_driver()))


    if __name__ == '__main__':
        main()
