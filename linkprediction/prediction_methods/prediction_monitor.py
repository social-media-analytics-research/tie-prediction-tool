from linkprediction.database_connector import DatabaseConnector


class PredictionMonitor(object):

    def __init__(self, worker, tasks):
        self.worker = worker
        self.tasks = tasks
        self.step_count = len(tasks)
        self.step = 1

    def notify(self, status):
        self._validate_status(status)

        monitoring_data = {
            'process_id': self.worker.process_id,
            'step_index': self.step,
            'max_steps': self.step_count,
            'name': self.tasks[self.step - 1]['name'],
            'status': status,
            'id_type': 'project_id',
            'reference_id': self.worker.project_id
        }

        self._update(monitoring_data)

        if status == 'Finished':
            self.step += 1

    def pending(self):
        monitoring_data = {
            'process_id': self.worker.process_id,
            'step_index': self.step,
            'max_steps': self.step_count,
            'name': 'Prediction',
            'status': 'Waiting',
            'id_type': 'project_id',
            'reference_id': self.worker.project_id
        }

        self._update(monitoring_data)        

    def finished(self):
        monitoring_data = {
            'process_id': self.worker.process_id,
            'step_index': self.step,
            'max_steps': self.step_count,
            'name': 'Prediction',
            'status': 'Finished',
            'id_type': 'project_id',
            'reference_id': self.worker.project_id
        }

        self._update(monitoring_data)

    def failed(self):
        monitoring_data = {
            'process_id': self.worker.process_id,
            'step_index': self.step,
            'max_steps': self.step_count,
            'name': 'Prediction',
            'status': 'Failed',
            'id_type': 'project_id',
            'reference_id': self.worker.project_id
        }

        self._update(monitoring_data)

    def _update(self, data):
        DatabaseConnector.get_db_instance().add_linkprediction_status(
            data['process_id'],
            data['step_index'],
            data['max_steps'],
            data['name'],
            data['status'],
            data['id_type'],
            data['reference_id']
        )

    def _validate_status(self, status):
        allowed_values = ["Waiting", "Processing", "Finished", "Failed"]
        if status not in allowed_values:
            raise ValueError(
                "Invalid value for `state` ({0}), must be one of {1}"
                .format(status, allowed_values)
            )
