from collections import deque

from fastapi import FastAPI 
from pydantic import BaseModel 
import uuid
import time 
from threading import Lock 
from typing import Optional 

import json
import os 
from pathlib import Path 

RESULTS_FILE = Path("results.json") 



def save_result_to_disk(task_id: str, result: str, status:str, worker_id:str):
  if os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, 'r') as f:
      results = json.load(f)
  else:
    results = [] 


  results.append({
    'task_id': task_id, 
    'result': result, 
    'status': status,
    'worker_id': worker_id, 
    'timestamp': time.time()
  })

  with open(RESULTS_FILE, 'w') as f:
    json.dump(results, f, indent=2) 

  
app = FastAPI() 

'''
task
  - id_task: str 
  - cd_status: str 
  - dt_claimed_at: timestamp 
  - dict_data: dict 

tasks 
  - task: list[task] 

queue 
  - id_tasks: list[str] 

lock = Lock()
''' 

TIMEOUT = 30 

tasks = dict() 
queue = deque() 
lock = Lock() 


class TaskSubmit(BaseModel):
  data: dict 

class TaskComplete(BaseModel):
  worker_id: str 
  result: str 


@app.post('/submit')
def submit_task(task: TaskSubmit):
  id_task = str(uuid.uuid4())

  with lock:
    tasks[id_task] = {
      'status': 'pending', 
      'data': task.data, 
      'dt_claimed_at': None, 
      'result': None
      }

    queue.append(id_task) 
  
  return {'task_id': id_task}


@app.get('/claim')
def claim_task():
  with lock: 
    for id_task, task in tasks.items():
      if task['status'] == 'processing':
        # Signifies worker is processing task 
        if time.time() - task['dt_claimed_at'] > TIMEOUT:
          # If task hasn't completed within timeout, reassign to queue
          task['status'] = 'pending' 
          queue.append(id_task) 
    

    if not queue:
      return {'task': None} 

    curr_task_id = queue.popleft() 
    tasks[curr_task_id]['status'] = 'processing' 
    tasks[curr_task_id]['dt_claimed_at'] = time.time() 

    return {
      'task': {
        'task_id': curr_task_id,
        'data': tasks[curr_task_id]['data']
      }
    }


@app.post('/complete/{id_task}')
def complete_task(id_task:str, completion: TaskComplete):
  with lock:
    if id_task in tasks:
      tasks[id_task]['status'] = 'completed' 
      tasks[id_task]['result'] = completion.result  
  save_result_to_disk(id_task, completion.result, 'completed', completion.worker_id)
  return {'status': 'ok'} 


if __name__=='__main__':
  import uvicorn 
  uvicorn.run(app, host='0.0.0.0', port =5001)
  
