import requests
import random 

SERVER_URL = "http://localhost:5001" 

def submit_task(num1, num2, operation):
  data = {'num1': num1, 'num2': num2, 'operation': operation}
  res = requests.post(f"{SERVER_URL}/submit", json={'data': data}) 
  return res.json().get('task_id') 


for i in range(10):
  num1 = random.randint(1, 100) 
  num2 = random.randint(1, 100) 
  operation = random.choice(['add', 'subtract', 'multiply', 'divide']) 
  task_id = submit_task(num1, num2, operation) 
  print(f"Submitted task {task_id} with data: {num1} {operation} {num2}")


