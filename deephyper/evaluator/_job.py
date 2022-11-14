import copy

from typing import Hashable

from deephyper.evaluator.storage import Storage


class Job:
    """Represents an evaluation executed by the ``Evaluator`` class.

    Args:
        id (Any): unique identifier of the job. Usually an integer.
        config (dict): argument dictionnary of the ``run_function``.
        run_function (callable): function executed by the ``Evaluator``
    """

    # Job status states.
    READY = 0
    RUNNING = 1
    DONE = 2

    def __init__(self, id, config: dict, run_function):
        self.id = id
        self.rank = None
        self.config = copy.deepcopy(config)
        self.run_function = run_function
        self.timestamp_start = None  # in seconds
        self.timestamp_end = None  # in seconds
        self.timestamp_submit = None  # in seconds
        self.timestamp_gather = None  # in seconds
        self.status = self.READY
        self.result = None  # objective values
        self.other = None  # other data returned to be logged
        self.budget = None  # consumed budget

    def __repr__(self) -> str:
        if self.rank is not None:
            return f"Job(id={self.id}, rank={self.rank}, status={self.status}, config={self.config})"
        else:
            return f"Job(id={self.id}, status={self.status}, config={self.config})"

    def __getitem__(self, index):
        cfg = copy.deepcopy(self.config)
        return (cfg, self.result)[index]


class RunningJob:
    def __init__(self, id: Hashable, parameters: dict, storage: Storage) -> None:
        self.id = id
        self.parameters = parameters
        self.storage = storage

    def __getitem__(self, k):
        return self.parameters[k]
