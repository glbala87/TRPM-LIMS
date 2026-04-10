"""
TRPM-LIMS load test suite.

Usage:
    pip install locust
    locust --host=http://localhost:8000

Simulates typical lab workflows: JWT login, patient listing, sample creation,
result queries.
"""
from locust import HttpUser, task, between


class LIMSUser(HttpUser):
    """Simulates an authenticated LIMS technician."""

    wait_time = between(1, 5)
    token = None

    def on_start(self):
        """Authenticate via JWT to get an access token."""
        resp = self.client.post('/api/auth/token/', json={
            'username': 'loadtest',
            'password': 'LoadTest-Pass-123!',
        })
        if resp.status_code == 200:
            self.token = resp.json().get('access')
        else:
            # If the test user doesn't exist, skip authenticated tasks.
            self.token = None

    @property
    def _headers(self):
        if self.token:
            return {'Authorization': f'Bearer {self.token}'}
        return {}

    @task(5)
    def list_patients(self):
        self.client.get('/api/patients/', headers=self._headers)

    @task(3)
    def list_lab_orders(self):
        self.client.get('/api/lab-orders/', headers=self._headers)

    @task(2)
    def list_molecular_samples(self):
        self.client.get('/api/molecular-samples/', headers=self._headers)

    @task(2)
    def list_results(self):
        self.client.get('/api/molecular-results/', headers=self._headers)

    @task(1)
    def list_reagents(self):
        self.client.get('/api/reagents/', headers=self._headers)

    @task(1)
    def list_equipment(self):
        self.client.get('/api/instruments/', headers=self._headers)

    @task(1)
    def api_schema(self):
        """Hit the schema endpoint — a cold-cache proxy for "heavy" requests."""
        self.client.get('/api/schema/', headers=self._headers)
