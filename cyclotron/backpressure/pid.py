from collections import namedtuple
import rx
import rx.operators as ops

from cyclotron.debug import trace_observable


PidContext = namedtuple('PidContext', ['last_error', 'control_value'])


def compute_pid(error, last_error, p, i, d):
    i_error = error + last_error
    d_error = error - last_error
    # print("p: {}, i: {}, d: {}".format(error, i_error, d_error))
    # print("p: {}, i: {}, d: {}".format(p*error, i*i_error, d*d_error))
    # print(p*error + i*i_error + d*d_error)
    return p*error + i*i_error + d*d_error


def pid(setpoint, p, i, d):
    '''
    Args:
        setpoint: An observable emiting setpoint values
        p: proportional component value
        i: integral component value
        d: derivative component value
    '''
    def _pid_step(acc, ii):
        setpoint = ii[1]
        process_value = ii[0]
        error = setpoint - process_value
        last_error = acc.last_error if acc is not None else 0
        control_value = compute_pid(error, last_error, p, i, d)

        return PidContext(
            last_error=error,
            control_value=control_value,
        )

    def _pid(process):
        return process.pipe(
            # trace_observable("pid"),
            ops.with_latest_from(setpoint),
            # trace_observable("pid2"),
            ops.scan(_pid_step, seed=None),
            # trace_observable("pid3"),
            ops.map(lambda i: i.control_value),
        )

    return _pid
