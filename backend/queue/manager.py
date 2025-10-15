# import multiprocessing
#
# _manager = None
# _task_queue = None
# _task_store = None
#
#
# def _initialize_manager():
#     """
#     A private function to initialize the manager and shared objects
#     if they haven't been created yet. This ensures it only runs once.
#     """
#     global _manager, _task_queue, _task_store
#
#     if _manager is None:
#         _manager = multiprocessing.Manager()
#         _task_queue = _manager.Queue()
#         _task_store = _manager.dict()
#
#
# def get_task_queue():
#     """
#     Returns the single, shared task queue instance.
#     Initializes the manager on first call.
#     """
#     _initialize_manager()
#     return _task_queue
#
#
# def get_task_store():
#     """
#     Returns the single, shared task store dictionary.
#     Initializes the manager on first call.
#     """
#     _initialize_manager()
#     return _task_store
