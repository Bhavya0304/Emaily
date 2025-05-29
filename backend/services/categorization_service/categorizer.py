import sys
import os
sys.dont_write_bytecode = True
from celery import Celery
from services.categorization_service.modelv1 import Categorize
from helper import load_env
from helper.logger import SingletonLogger,LogTypes

load_env.Load()

# Configure Celery with RabbitMQ (or Redis if you prefer)
app = Celery(
    'categorizer',
    broker=os.getenv('BROKER_URL'),  # Replace with Redis URL if using Redis
)

@app.task(name='tasks.categorize_email')
def categorize_email(email_data, categories, min_threshold=30,message_id = None,account_id = None):
    try:
        result = Categorize(email_data, categories, min_threshold,message_id,account_id)
        return result
    except Exception as e:
        SingletonLogger.get_logger().Log(LogTypes.Gmail,str(e))