"""The callback module contains sub-classes of the ``Callback`` class used to trigger custom actions on the start and completion of jobs by the ``Evaluator``. Callbacks can be used with any Evaluator implementation.
"""
import numpy as np

import pandas as pd
from tqdm import tqdm
from deephyper.core.exceptions import SearchTerminationError


class Callback:
    def on_launch(self, job):
        """Called each time a ``Job`` is created by the ``Evaluator``.

        Args:
            job (Job): The created job.
        """
        ...

    def on_done(self, job):
        """Called each time a Job is completed by the Evaluator.

        Args:
            job (Job): The completed job.
        """
        ...


class ProfilingCallback(Callback):
    """Collect profiling data. Each time a ``Job`` is completed by the ``Evaluator`` a the different timestamps corresponding to the submit and gather (and run function start and end if the ``profile`` decorator is used on the run function) are collected.

    An example usage can be:

    >>> profiler = ProfilingCallback()
    >>> evaluator.create(method="ray", method_kwargs={..., "callbacks": [profiler]})
    ...
    >>> profiler.profile
    """

    def __init__(self):
        self.history = []

    def on_launch(self, job):
        ...

    def on_done(self, job):
        start = job.timestamp_submit
        end = job.timestamp_gather
        if job.timestamp_start is not None and job.timestamp_end is not None:
            start = job.timestamp_start
            end = job.timestamp_end
        self.history.append((start, 1))
        self.history.append((end, -1))

    @property
    def profile(self):
        n_jobs = 0
        profile = []
        for t, incr in sorted(self.history):
            n_jobs += incr
            profile.append([t, n_jobs])
        cols = ["timestamp", "n_jobs_running"]
        df = pd.DataFrame(profile, columns=cols)
        return df


class LoggerCallback(Callback):
    """Print information when jobs are completed by the ``Evaluator``.

    An example usage can be:

    >>> evaluator.create(method="ray", method_kwargs={..., "callbacks": [LoggerCallback()]})
    """

    def __init__(self):
        self._best_objective = None
        self._n_done = 0

    def on_done(self, job):
        self._n_done += 1
        if np.isreal(job.result):
            if self._best_objective is None:
                self._best_objective = job.result
            else:
                self._best_objective = max(job.result, self._best_objective)

            print(
                f"[{self._n_done:05d}] -- best objective: {self._best_objective:.5f} -- received objective: {job.result:.5f}"
            )
        elif type(job.result) is str and "F" == job.result[0]:
            print(f"[{self._n_done:05d}] -- received failure: {job.result}")

class TqdmCallback(Callback):
    """Print information when jobs are completed by the ``Evaluator``.

    An example usage can be:

    >>> evaluator.create(method="ray", method_kwargs={..., "callbacks": [LoggerCallback()]})
    """

    def __init__(self, max_evals):
        self._best_objective = None
        self._n_done = 0
        self._tqdm = tqdm(total=max_evals)

    def on_done(self, job):
        self._n_done += 1
        self._tqdm.update(1)
        if np.isreal(job.result):
            if self._best_objective is None:
                self._best_objective = job.result
            else:
                self._best_objective = max(job.result, self._best_objective)
        self._tqdm.set_postfix(objective=self._best_objective)


class SearchEarlyStopping(Callback):
    """Stop the search gracefully when it does not improve for a given number of evaluations.

    Args:
        patience (int, optional): The number of not improving evaluations to wait for before stopping the search. Defaults to 10.
        objective_func (callable, optional): A function that takes a ``Job`` has input and returns the maximized scalar value monitored by this callback. Defaults to ``lambda j: j.result``.
    """

    def __init__(self, patience: int = 10, objective_func=lambda j: j.result):
        self._best_objective = None
        self._n_lower = 0
        self._patience = patience
        self._objective_func = objective_func

    def on_done(self, job):
        job_objective = self._objective_func(job)
        if self._best_objective is None:
            self._best_objective = job_objective
        else:
            if job_objective > self._best_objective:
                print(
                    f"Objective has improved from {self._best_objective:.5f} -> {job_objective:.5f}"
                )
                self._best_objective = job_objective
                self._n_lower = 0
            else:
                self._n_lower += 1

        if self._n_lower >= self._patience:
            print(
                f"Stopping the search because it did not improve for the last {self._patience} evaluations!"
            )
            raise SearchTerminationError
