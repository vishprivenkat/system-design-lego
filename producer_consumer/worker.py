import requests 
import time 
import uuid 

SERVER_URL = "http://localhost:5001"
POLL_INTERVAL = 2 
WORKER_ID = str(uuid.uuid4()) 

def process_task(task_data):
  num1 = task_data['num1'] 
  num2 = task_data['num2'] 
  operation = task_data['operation'] 
  print(f"Processing task: {num1} {operation} {num2}") 
  res = 0 
  if operation == 'add':
    res = num1 + num2 
  elif operation == 'subtract':
    res = num1 - num2 
  elif operation == 'multiply':
    res = num1 * num2 
  elif operation == 'divide':
    res = num1 / num2 if num2 != 0 else None
  return str(res) 


def main():
  print(f"Worker {WORKER_ID} started, polling for tasks...") 

  while True: 
    try:
      resp = requests.get(f"{SERVER_URL}/claim") 
      resp_data = resp.json() 

      if resp_data.get('task'): 
        task_id = resp_data['task']['task_id'] 
        task_data = resp_data['task']['data'] 
        result = process_task(task_data) 

        requests.post(f"{SERVER_URL}/complete/{task_id}", json={'result': result, 'worker_id': WORKER_ID}) 
        print(f"Completed task {task_id} with result: {result}") 
      else:
        print("No tasks available, waiting...") 
        time.sleep(POLL_INTERVAL)
    
    except Exception as e:
      print(f"Error Occurred: {e}") 
      time.sleep(POLL_INTERVAL) 


if __name__ == "__main__":
  main()