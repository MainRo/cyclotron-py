from collections import namedtuple
import rx
import rx.operators as ops

from cyclotron.debug import trace_observable


PidContext = namedtuple('PidContext', ['last_error', 'control_value'])


def compute_pid(error, last_error, p, i, d):
    i_error = error + last_error
    d_error = error - last_error
    return p*error + i*i_error + d*d_error


def pid(setpoint, process_value, p, i, d, t, scheduler=None):
    '''
    Args:
        setpoint: An observable emiting setpoint values
        process_value: An observabe emiting process values
        p: proportional component value
        i: integral component value
        d: derivative component value
        t: samling period in seconds
        scheduler: scheduler used to run the timer
    '''
    def _pid(acc, ii):
        setpoint = ii[1]
        process_value = ii[2]
        error = process_value - setpoint
        last_error = acc.last_error if acc is not None else 0
        control_value = compute_pid(error, last_error, p, i, d)

        return PidContext(
            last_error=error,
            control_value=control_value,
        )

    '''
    process_value = process_value.pipe(
        trace_observable("pid process"),
    )

    setpoint = setpoint.pipe(
        trace_observable("pid setpoint"),
    )
    '''

    return rx.timer(duetime=t, period=t, scheduler=scheduler).pipe(
        # trace_observable("pid"),
        ops.with_latest_from(setpoint, process_value),
        # trace_observable("pid2"),
        ops.scan(_pid, seed=None),
        # trace_observable("pid3"),
        ops.map(lambda i: i.control_value),
    )
