import copy
from typing import Any, Dict, Hashable, List, Tuple

from deephyper.evaluator.storage._storage import Storage


class MemoryStorage(Storage):
    def __init__(self) -> None:
        super().__init__()

        self._search_id_counter = 0
        self._data = {}

    def create_new_search(self) -> Hashable:
        """Create a new search in the store and returns its identifier.

        Returns:
            Hashable: The identifier of the search.
        """
        search_id = f"{self._search_id_counter}"  # converting to str
        self._search_id_counter += 1
        self._data[search_id] = {"job_id_counter": 0, "data": {}}
        return search_id

    def create_new_job(self, search_id: Hashable) -> Hashable:
        """Creates a new job in the store and returns its identifier.

        Args:
            search_id (Hashable): The identifier of the search in which a new job
            is created.

        Returns:
            Hashable: The created identifier of the job.
        """
        partial_id = self._data[search_id]["job_id_counter"]
        partial_id = f"{partial_id}"  # converting to str
        job_id = f"{search_id}.{partial_id}"
        self._data[search_id]["job_id_counter"] += 1
        self._data[search_id]["data"][partial_id] = {
            "in": None,
            "out": None,
            "metadata": {},
        }
        return job_id

    def store_job(self, job_id: Hashable, key: Hashable, value: Any) -> None:
        """Stores the value corresponding to key for job_id.

        Args:
            job_id (Hashable): The identifier of the job.
            key (Hashable): A key to use to store the value.
            value (Any): The value to store.
        """
        search_id, partial_id = job_id.split(".")

        self._data[search_id]["data"][partial_id][key] = value

    def store_job_in(
        self, job_id: Hashable, args: Tuple = None, kwargs: Dict = None
    ) -> None:
        """Stores the input arguments of the executed job.

        Args:
            job_id (Hashable): The identifier of the job.
            args (Optional[Tuple], optional): The positional arguments. Defaults to None.
            kwargs (Optional[Dict], optional): The keyword arguments. Defaults to None.
        """
        self.store_job(job_id, key="in", value={"args": args, "kwargs": kwargs})

    def store_job_out(self, job_id: Hashable, value: Any) -> None:
        """Stores the output value of the executed job.

        Args:
            job_id (Hashable): The identifier of the job.
            value (Any): The value to store.
        """
        self.store_job(job_id, key="out", value=value)

    def store_job_metadata(self, job_id: Hashable, key: Hashable, value: Any) -> None:
        """Stores other metadata related to the execution of the job.

        Args:
            job_id (Hashable): The identifier of the job.
            key (Hashable): A key to use to store the metadata of the given job.
            value (Any): The value to store.
        """
        search_id, partial_id = job_id.split(".")
        self._data[search_id]["data"][partial_id]["metadata"][key] = value

    def load_all_search_ids(self) -> List[Hashable]:
        """Loads the identifiers of all recorded searches.

        Returns:
            List[Hashable]: A list of identifiers of all the recorded searches.
        """
        return list(self._data.keys())

    def load_all_job_ids(self, search_id: Hashable) -> List[Hashable]:
        """Loads the identifiers of all recorded jobs in the search.

        Args:
            search_id (Hashable): The identifier of the search.

        Returns:
            List[Hashable]: A list of identifiers of all the jobs.
        """
        partial_ids = self._data[search_id]["data"].keys()
        job_ids = [f"{search_id}.{p_id}" for p_id in partial_ids]
        return job_ids

    def load_search(self, search_id: Hashable) -> dict:
        """Loads the data of a search.

        Args:
            search_id (Hashable): The identifier of the search.

        Returns:
            dict: The corresponding data of the search.
        """
        data = self._data[search_id]["data"]
        return copy.deepcopy(data)

    def load_job(self, job_id: Hashable) -> dict:
        """Loads the data of a job.

        Args:
            job_id (Hashable): The identifier of the job.

        Returns:
            dict: The corresponding data of the job.
        """
        search_id, partial_id = job_id.split(".")
        data = self._data[search_id]["data"][partial_id]
        return copy.deepcopy(data)
