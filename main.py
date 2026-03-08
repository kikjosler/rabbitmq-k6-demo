from fastapi import FastAPI, BackgroundTasks
import aio_pika
import asyncio
import json
from pydantic import BaseModel
import os

app = FastAPI(title="RabbitMQ Producer API")

class Order(BaseModel):
    order_id: str
    customer: str
    amount: float

async def send_to_rabbitmq(message: dict):
    """Отправляет заказ в очередь orders"""
    rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    connection = await aio_pika.connect_robust(rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue("orders")
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key="orders"
        )
        print(f"🚀 Order {message['order_id']} → RabbitMQ")

@app.post("/orders")
async def create_order(order: Order, background_tasks: BackgroundTasks):
    """Создаёт заказ → RabbitMQ (fire & forget)"""
    background_tasks.add_task(send_to_rabbitmq, order.dict())
    return {"status": "order_accepted", "order_id": order.order_id}

@app.get("/health")
async def health():
    return {"status": "healthy", "rabbitmq": "connected"}
