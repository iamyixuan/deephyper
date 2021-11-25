import copy
import logging

from deephyper.evaluator._evaluator import Evaluator

ray_initializer = None

logger = logging.getLogger(__name__)


class SerialEvaluator(Evaluator):
    """This evaluator run evaluations one after the other (not parallel).

    Args:
        run_function (callable): functions to be executed by the ``Evaluator``.
        num_workers (int, optional): Number of parallel Ray-workers used to compute the ``run_function``. Defaults to 1.
        callbacks (list, optional): A list of callbacks to trigger custom actions at the creation or completion of jobs. Defaults to None.
    """

    def __init__(
        self,
        run_function,
        num_workers: int = 1,
        callbacks=None,
        
    ):
        super().__init__(run_function, num_workers, callbacks)

        self.num_workers = num_workers

        logger.info(
            f"Serial Evaluator will execute {self.run_function.__name__}() from module {self.run_function.__module__}"
        )

    async def execute(self, job):

        sol = self.run_function(copy.deepcopy(job.config))

        job.result = sol

        return job
