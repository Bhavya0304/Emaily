from celery import Celery
from modelv1 import Categorize

# Configure Celery with RabbitMQ (or Redis if you prefer)
app = Celery(
    'categorizer',
    broker='amqp://guest:guest@localhost:5672//',  # Replace with Redis URL if using Redis
)

@app.task(name='tasks.categorize_email')
def categorize_email(email_data, categories, min_threshold=30,user_data = None):
    result = Categorize(email_data, categories, min_threshold,user_data)
    return result