from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
# from langchain.output_parsers import StrOutputParser
import pandas as pd
import numpy as np
import uuid
import textwrap
import json
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS, cross_origin
# Initialize the OpenAI Chat model
import os
import time

           
llm = ChatOpenAI(model='gpt-4o-mini',temperature = 0)



import requests
import base64
import json
import os
import json
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import base64
import requests
global ins_conversation_history

# Initialize conversation history
conversation_history = []
output_generation_history = []
ins_conversation_history = []

import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
import numpy as np

reasoning_test = """Assume the laws of physics on Earth. 
                    A small marble is put into a normal cup and the cup is placed upside down on a table. 
                    Someone then takes the cup without changing its orientation and puts it inside the microwave. 
                    Where is the marble now?"""

def task_complexity_check(task, main_task):
    # Define a chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You will be given a sub-task, and the main task for context. (Assume the sub-task is the main task if no main task is given)

        Your one and only goal is to determine if the task in hand is meant for multi-step reasoning or can be answered immediately using the information
 
        
         Here are some tips that will help you make a decision:
        
        1) Always return False if it's the main task, unless its very very obvious trivia type of question
        2) If it's not the main task, you should really be conservative in splitting it(returning False) unless you really think splitting it would give added benefits. So most times you'll end up returning True, unless obviosly its the main task, then you mostly return False.
        3) If the task is about executing a small bunch of code, return True
        
        Then, return True if want to split the task, else return False. 
        """),
        ("user", "SUB - Task Description: {input}  Main Task - {main_task}")
    ])
    
    # Combine the prompt and the LLM in a chain, add a string output parser
    chain = prompt | llm 
    
    # Run the chain with an example input
    
    result = chain.invoke({"input": task, "main_task" : main_task})
    # print(result)
    return result.content

def perform_task_python(task, previous_answers="No Previous Answers", main_task_context="This is the main task"):

    # Define a chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You will be given a simple sub-task related to python, reference to the main task, and trustable data context. 
        
        Your task is to do the sub-task ONLY, use any other information only for reference.

        You will also be given the answers for the other subtasks for reference. 
        
        Perform the task and return the answer as python pandas code. Make sure to be on the point and briefly explain what the answer is that your are returning.
        """),
        ("user",  "SUB-TASK to do(Do not perform any other TASK apart from this!!!!): {input} \n\nMain Context(don't do the other tasks) : {main_task_context} \n\nPrevious Answers: {previous_answers}  ")
    ])
    
    # Combine the prompt and the LLM in a chain, add a string output parser
    chain = prompt | llm 
    
    # Run the chain with an example input
    result = chain.invoke({"input": task, "main_task_context" : main_task_context, "previous_answers" : previous_answers})
    # print(result)
    return result.content

def finetune_code(task, code):
    # Define a chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You will be given a task and a bunch of python code written to find a trustable answer, 

        Your task is to convert these lines of code into a function named "test_function" which returns the required answer of the task as output. The answer that the function return must precisely answer the question without at any other context or translation. 
        It's okay to be concise, but the answer needs the be there. 

        Never ever return multiple arguments. If you have multiple variables as answers, combine them in a meaningful way.
        
        Make sure to only return code as exactly what you return will be executed in a python compiler.
        """),
        ("user", "main task : {task} \n\n code : {code}")
    ])
    
    # Combine the prompt and the LLM in a chain, add a string output parser
    chain = prompt | llm 
    
    # Run the chain with an example input
    
    result = chain.invoke({"task" : task, "code": code})
    # print(result)
    return result.content

def execute_code(code_string):
    local_context = {}
    global_context = {
        'pd': pd
    }
    
    try:
        exec(code_string, global_context, local_context)
        # Debugging output to check what's in local_context after exec
        print("Local context keys:", local_context.keys())
    except Exception as e:
        print("Error during exec:", e)
        return None
    
    # Check if 'test_function' is correctly defined in local_context
    if 'test_function' in local_context:
        test_function = local_context['test_function']
        # Execute the function and return the result
        return test_function()
    else:
        print("test_function is not defined in the code string.")
        return None


def perform_and_return_answer(task):
    answer_text = perform_task_python(task, previous_answers="No Previous Answers")
    answer_code = finetune_code(task,answer_text)
    print(answer_code)
    code_result = execute_code(answer_code.replace("```","").replace("python",""))
    print("Final Code Result")
    print(code_result)
    return str(code_result)

def perform_task(task,previous_answers = "No Previous Answers", main_task_context = "This is the main task"):
    # Define a chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a logical genius. You will be given a simple sub-task to do, a reference to the parent task and trustable data context. Your task is to do the sub-task and sub-task only, use any other information only for reference.

        You will also be given the answers for the other subtasks for reference. Do not do the main task in any case.

        MAKE SURE YOU ARE ONLY AND ONLY PERFORMING THE SUB TASK GIVEN TO YOU, BUT IN THE CONTEXT OF THE MAIN TASK, CONSIDERING THE OTHER SUB TASKS FOR REFERENCE IF REQUIRED
        
        Think about it logical and considering the the question given Perform the task and return the answer. Make sure to be on the point and briefly explain what the answer is that your are returning, but make sure you are returning the data
        """),
        ("user", "SUB-TASK to do(Do not perform any other TASK apart from this!!!!): {input}  \n\nMain Context(don't do the other tasks) : {main_task_context} \n\nPrevious Answers: {previous_answers}  ")
    ])
    
    # Combine the prompt and the LLM in a chain, add a string output parser
    chain = prompt | llm 
    
    # Run the chain with an example input
    
    result = chain.invoke({"input": task,"main_task_context" : main_task_context, "previous_answers" : previous_answers})
    # print(result)
    return result.content

def checks_generation(task):
    # Define a chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You will be given a question. Assumming that there has been an answer generated for the question, what are the checks
        we can have in place to make sure that the answer is right beyond any doubt - even using python code and internet browsing if required?
         
        Definition of a test - A scientifically provable question that is as specific as possible. 
         
        A test can be ONLY be proved using 3 ways:
         
        Trustable ways - If answer can be validated using these ways, pick it without doubt
        
        1) Python interpreter - A Python interpreter can be used to validate the answer without doubt
        2) Wikipedia - Wikipedia can be used to validate the answer without doubt
         
        Ambigious Ways - Only if other ways don't work, use this
        
        3) Logical Analysis - Logical rules can be used check if the answer is right
        
        Assume that any source of information used to retrieve the information is accurate, no need to ask for sources too.

        MAKE SURE EVERY CHECK IS UNIQUE AND THAT ONE CHECK NEVER DOES WHAT ANY OTHER CHECK DOES
                 
        Example :
        
        Input - What is the answer to this `example-puzzle with condition 1,2,3....n`?

        OUtput - 1) Does the answer meet the condition 1? This can be proved by Wikipedia
                2) Does the answer meet the condition 2? This can be proved using python
                3) Does the answer meet the condition 3? This can be proved using logic
                ....
                n) Does the answer meet the condition 3?
   

        PLEASE OUTPUT THE MINIMUM QUANTITY OF CHECKS. THE IDEAL QUANITY IS ONE, ONLY USE MORE IF ABSOLUTELY REQUIRED.      
        """),
        ("user", "{input}")
    ])
    
    # Combine the prompt and the LLM in a chain, add a string output parser
    chain = prompt | llm 
    
    # Run the chain with an example input
    
    result = chain.invoke({"input": task})
    # print(result)
    return result.content

def task_generation(task,checks):
    # Define a chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You will be given a question, and the tests to check the answer.

        Your task is to return the smallest number of tasks to do to answer the question, making sure to use the hints given in tests to draft HIGHLY SPECIFIC task descriptions.
         
        The tasks must be generated in a step-by-step format in such a way, that each tasks answer will feed into the next one and together they will reach the final goal. 
         

        VERY IMPORTANT - NO SUB-TASK SHOULD EVER BE ABOUT CHECKING ANYTHING. CHECKING WILL BE DONE IN A LATER STAGE ANYWAY. DO NOT USE WORDS LIKE ANALYZE, OBSERVE, EXPLAIN, CONFIRM. 


        
        Example 1 - 

        Input - Question - What is the alternative name of the capital of the biggest state in India?
                
                Checks - 1) Is this place in the largest state in India according to wikipedia?
                        2) Is this place the capital of the largest state in India according to wikipedia?
                        3) Is this place the alternative name of the capital of the largest state in India according to wikipedia?

        Output - 1) Determine the largest state in India using Wikipedia
                2) Determine the capital of the largest state in India using Wikipedia
                3) Determine the alternative name of the capital city of the largest state in India using Wikipedia

        
         
        Example 2 - 

        
        Input - Question - Which state/states in the US has/have the largest number of the letter a's in its/their name/names?
                
                Checks - 1) Is this state in the US? - Can be checked using Wikipedia
                        2) Does this state have more a's in its name comapared to the other states names? - Can be verified using python

        Output - 1) Extract the names of all the states in US according using Wikipedia
                2) Rank the states according to highest number of a's in their name and return the state/states with highest number  - using python

         
        
         
         
        Example 3 - 

        Input - Question - Sally wants to stack 6 cubed blocks of wood to form a structure that look like its escalating the most, what is the way to do this? Each block must sit squarely on another one, no placing it halfway.
                
                Checks - 1) Using the suggest answer, do the block structure look like it's escalating? - Can be checked by visualizing the structure using python and analysing the image of the structure using image APIs
                        2) Are only 6 blocks being used? - Can be checked using python
                        3) Are any of the blocks being placed half way? - Can be determined by reading the answer

        Output - 1) Use python to come up with ways to visualize multiple orientations of placing 6 cubed blocks of wood, 
                2) Determine all the structures that look like they're escalating
                3) Define a metric of measuring escalation
                4) Rank the orientations in order of escalation and return the most escalating looking orientation
        
         
         
         
        Return a numbered list of these tasks and remember to never duplicate a task. Every task must be unique and you should use the smallest number of tasks.
        """),
        ("user", "task : {task}, checks : {checks}")
    ])
    
    # Combine the prompt and the LLM in a chain, add a string output parser
    chain = prompt | llm 
    
    # Run the chain with an example input
    
    result = chain.invoke({"task": task,"checks" : checks})
    # print(result)
    return result.content

def task_ordering(task,sub_tasks):
    # Define a chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You will be given a task and list of sub-tasks related to that one task
        
        You have three goals:

        First Goal - Order the list such that it follows how a normal human would do these set of tasks

        Second Goal - Remove any tasks that are duplicated and say the same thing that other tasks say. NUMBER OF TASKS MUST BE MINIMISED AS MUCH AS POSSIBLE.

        Third Goal - Ensure that the tasks contain reference to the results of other tasks wherever needed


        Return only and ONLY a numbered list of the sub-tasks
        """),
        ("user", "task : {task}, sub_tasks : {sub_tasks}")
    ])
    
    # Combine the prompt and the LLM in a chain, add a string output parser
    chain = prompt | llm 
    
    # Run the chain with an example input
    
    result = chain.invoke({"task": task,"sub_tasks" : sub_tasks})
    # print(result)
    return result.content.split('\n')

def aggregate_answers(task, answers):
    # Define a chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You will be given a task and an aggregated answer which is the summation of a bunch of sub-tasks created from the task.

        Your only task is to consider the answers for all the subtasks and return the final answer
        """),
        ("user", "task : {task}, full_answer : {answers}")
    ])
    
    # Combine the prompt and the LLM in a chain, add a string output parser
    chain = prompt | llm 
    
    # Run the chain with an example input
    
    result = chain.invoke({"task": task,"answers" : answers})
    # print(result)
    return result.content
    
def check_answer(task, answer, check):
    # Define a chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You will be given a task, the answer to the task and a specific thing to check about the answer.

        Assume all sources of the data are perfectly accurate and up to date

        Return True if the answer meets the check, if not return false
        """),
        ("user", "task : {task}, answer : {answers}, check : {check}")
    ])
    
    # Combine the prompt and the LLM in a chain, add a string output parser
    chain = prompt | llm 
    
    # Run the chain with an example input
    
    result = chain.invoke({"task": task,"answers" : answer,"check" : check})
    # print(result)
    return result.content

def fix_answer(test, answer, check):
    # Define a chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You will be given the description of a task, it's answer and a test that the answer failed. 

    
        Your task is to return the correct code that actually passes the test

        THE NEW ANSWER MUST ONLY RETURN ONE DATAFRAME/ANSWER. DO NOT EVER RETURN MULTIPLE ARGUMENTS.

        If you have to return multiple dataframe, make sure that they are combined in a meaningful way.

        """),
        ("user", "Main Task : {task}, Answer : {answer}, Test that the answer failed : {check}")
    ])
    
    # Combine the prompt and the LLM in a chain, add a string output parser
    chain = prompt | llm 
    
    # Run the chain with an example input
    
    result = chain.invoke({"task": task, "answer" : answer,"check" : check})
    # print(result)
    return result.content

def shorten_answer(test, answer):
    # Define a chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You'll be given the description of a task and it's final confirmed answer. Your only goal is to return only the main answer without any extra words. Be extremely matter of fact and give me the direct answer.

        NEVER EVER SAY DATA IS NOT ENOUGH. I WANT YOU TO GIVE ONE WORD ANSWERS UNLESS YOU ABSOLUTELY NEED TO INCLUDE MORE WORDS. NEVER EVER DENY TO ANSWER.
        """),
        ("user", "Main Task : {task}, \n\n Answer : {answer}")
    ])
    
    # Combine the prompt and the LLM in a chain, add a string output parser
    chain = prompt | llm 
    
    # Run the chain with an example input
    
    result = chain.invoke({"task": test, "answer" : answer})
    # print(result)
    return result.content

def correct_or_not(answer):
    # Define a chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You will be given an answer to question. Your only task is to return "Correct" if the answer is about something being on a table and "Wrong" if it's anything else
        """),
        ("user", "Answer : {answer}")
    ])
    
    # Combine the prompt and the LLM in a chain, add a string output parser
    chain = prompt | llm 
    
    # Run the chain with an example input
    
    result = chain.invoke({"answer" : answer})
    # print(result)
    return result.content

def test_model(task,model):
    # Define a chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You will be given a logical question, think about it and give me the final answer
        """),
        ("user", "The logical question is: {task}")
    ])
    
    # Combine the prompt and the LLM in a chain, add a string output parser
    chain = prompt | model
    
    # Run the chain with an example input
    
    result = chain.invoke({"task": task})
    # print(result)
    return result.content

def check_and_fix_answer(task, initial_answer, checks, node_id, socket, max_retries=3):
    current_answer = initial_answer
    failed_tasks = checks.split('\n')
    retry_count = 0
    
    socket.emit('testUpdate', {'nodeId': node_id, 'passedTests': 0, 'totalTests': len(failed_tasks)})
    time.sleep(0.2)

    while failed_tasks and retry_count < max_retries:
        
        # Reset the list of failed tasks for this iteration
        new_failed_tasks = []
        
        
        for current_check in failed_tasks:
            answer_check = check_answer(task, current_answer, current_check)
            print(answer_check)
            if "False" in answer_check.lower():
                new_failed_tasks.append(current_check)
            else:
                continue
                # print(f"CHECK PASSED: {current_check}")

        socket.emit('testUpdate', {'nodeId': node_id, 'passedTests': len(failed_tasks) - len(new_failed_tasks), 'totalTests': len(failed_tasks)})
        time.sleep(0.2)

        if not new_failed_tasks:
            # All checks passed, return the current answer
            return current_answer
        
        # Fix the failed tasks
        for failed_check in new_failed_tasks:
            current_answer = fix_answer(failed_check, current_answer, check_answer)
        
        # Update the failed_tasks with the new list after fixing
        failed_tasks = new_failed_tasks
        retry_count += 1
        # print(f"Retry attempt {retry_count}")

    # Return the final answer after retries or if all tests passed
    return current_answer

def task_rru(task,socketio, previous_answers="No Previous Answers", main_task_context="This is the main task", node_id=None, parent_node_id = None):

    # Check if the data needs to be split
    task_doable = task_complexity_check(task,main_task_context)
        
    description_node_id = f"node-{str(uuid.uuid4())}"
    label = task

    print(socketio)
    

    if "true" in task_doable.lower():

        if parent_node_id:
            socketio.emit('update', {'id': description_node_id, 'label': label,'parentId': parent_node_id, 'type' : "subTask", 'hasTests': True})
        else:
            socketio.emit('update', {'id': description_node_id, 'label': label,'parentId': parent_node_id, 'type' : "mainTask", 'hasTests': True})
        time.sleep(0.2)
       
        if "python" in task.lower():
            task_answer = perform_and_return_answer(task)
            answer_type = "codeAnswer"
            answer_node_id = f"node-{str(uuid.uuid4())}"
            label = task_answer
            socketio.emit('update', {'id': answer_node_id, 'label': label,'parentId': description_node_id, 'type' : 'codeAnswer'})
            time.sleep(0.2)

        else:
        # If the task is not split, perform the task and return it
            task_answer = perform_task(task, previous_answers, main_task_context)
            answer_type = "answer"
            answer_node_id = f"node-{str(uuid.uuid4())}"
            label = task_answer
            socketio.emit('update', {'id': answer_node_id, 'label': label,'parentId': description_node_id, 'type' : 'answer'})
            time.sleep(0.2)
        
        
        
        return task_answer
    else:
        if parent_node_id:
            socketio.emit('update', {'id': description_node_id, 'label': label,'parentId': parent_node_id, 'type' : "subTask", 'hasTests': True})
        else:
            socketio.emit('update', {'id': description_node_id, 'label': label,'parentId': parent_node_id, 'type' : "mainTask", 'hasTests': True})
        time.sleep(0.2)
        # If the answer is to be split, first generate the tests
        checks = checks_generation(task)
        print("CHECKS: ")
        print(checks)
        # Generate sub-tasks using the tests as reference
        sub_tasks = task_generation(task, checks)
        

        # Order the sub-tasks and fix minor issues
        ordered_tasks = task_ordering(task, sub_tasks)
        print("ORDERED TASKS: ")
        print(ordered_tasks)

        # socketio.emit('testUpdate', {'nodeId': description_node_id, 'passedTests': 0, 'totalTests': len(checks)})      
        full_answer = ""
        mt_context = "Main Task Information: " + task + "\n" + '\n'.join(ordered_tasks)
        
        # Recursively call the same function on each of the sub-task
        for current in ordered_tasks:
            print('Sub-Task', current)
            sub_task_id = str(uuid.uuid4())
            temp_answer = task_rru(current, socketio, full_answer, mt_context, sub_task_id,description_node_id)
            full_answer += temp_answer + "\n"
            print(temp_answer)
        
        # Aggregate the individual sub-task answers
        answer = aggregate_answers(task, full_answer)
        print("AGGREGATE ANSWER")
        print(answer)
        # Check the answer on tests and fix it until all the tests pass
        checked_answer = check_and_fix_answer(task, answer, checks, description_node_id, socketio)
        # socketio.emit('testUpdate', {'nodeId': description_node_id, 'passedTests': len(checks), 'totalTests': len(checks)})
        print("CHECKED ANSWER")
        print(checked_answer)

        short_answer = shorten_answer(task, checked_answer)
        return short_answer
    



# result = task_rru(reasoning_test)
# print(result)


# def ARC_answer(json_file_path,socketio):
#     question_node_id = f"node-{str(uuid.uuid4())}"
#     label = f"Task"
#     print(socketio)
#     image_filename = "test_input.jpg_combined.jpg"
#     image_url = f"http://localhost:5020/backend-image/{image_filename}"  # URL to serve image

#     socketio.emit('update', {
#         'id': question_node_id,
#         'label': label,
#         'imageUrl': image_url,
#         'type' : "imageNode" # Send the image URL to the front-end
#     })
#     global conversation_history
#     global output_generation_history
#     global ins_conversation_history
#     # Initialize conversation history
#     conversation_history = []
#     output_generation_history = []
#     ins_conversation_history = []
#     with open(json_file_path) as f:
#         data = json.load(f)
#         data_str = f.read()

#     if 'test' in data and len(data['test']) > 0:
#         test_input = data['test'][0]['input']

#         image_path = 'test_input.jpg'
#         save_image(data, image_path)
#         save_image_with_numbers(data, image_path + "_numbered_")
#         data_new, test_o, test_i, output_format = remove_test_output(data)
#         print(data_new)
#         # print()

        
#         description = describe_image_via_gpt(image_path,data_new)
#         description_node_id = f"node-{str(uuid.uuid4())}"
#         label = f"Describe this pattern in this image"
#         print(socketio)
#         socketio.emit('update', {'id': description_node_id, 'label': label,'parentId': question_node_id, 'type' : "textUpdater"})
#         description_node_answer_id = f"node-{str(uuid.uuid4())}"
#         label = f"{description}"
#         print(socketio)
#         socketio.emit('update', {'id': description_node_answer_id, 'label': label,'parentId': description_node_id, 'type' : "displayNode"})
#         # print("SECOND DESCRIPTION: \n\n\n")
#         # print(description)
#         # print("\n\n\n\n")
        
#         answer_text = answer_lucidation()

#         answer_text_node_id = f"node-{str(uuid.uuid4())}"
#         label = f"Now think about what the pattern could be"
#         print(socketio)
#         socketio.emit('update', {'id': answer_text_node_id, 'label': label,'parentId': description_node_answer_id, 'type' : "textUpdater"})
        
#         answer_text_node_answer_id = f"node-{str(uuid.uuid4())}"
#         label = f"{answer_text}"
#         print(socketio)
#         socketio.emit('update', {'id': answer_text_node_answer_id, 'label': label,'parentId': answer_text_node_id, 'type' : "displayNode"})
        
        
#         answer_text_two = answer_lucidation_two()
        
#         answer_text_two_node_id = f"node-{str(uuid.uuid4())}"
#         label = f"Now try to clarify the pattern"
#         print(socketio)
#         socketio.emit('update', {'id': answer_text_two_node_id, 'label': label,'parentId': answer_text_node_answer_id, 'type' : "textUpdater"})
        
#         answer_text_two_node_answer_id = f"node-{str(uuid.uuid4())}"
#         label = f"Second Filter"
#         print(socketio)
#         socketio.emit('update', {'id': answer_text_two_node_answer_id, 'label': answer_text_two,'parentId': answer_text_two_node_id, 'type' : "displayNode"})
#         # print("ANSWER LUCIDATION : ")
#         # print(answer_text)
#         print("ANSWER TEXT: ")
#         print(answer_text)
#         print("\n\n ANSWER TEXT TWO: \n\n")
#         print(answer_text_two)
        
#         instruction_set = create_instruction_set(image_path, data_new)
#         print("INSTRUCTION SET:")
#         print(instruction_set)


#         instruction_set_node_id = f"node-{str(uuid.uuid4())}"
#         label = f"Instruction Set "
#         print(socketio)
#         socketio.emit('update', {'id': instruction_set_node_id, 'label': label,'parentId': answer_text_two_node_answer_id, 'type' : "textUpdater"})
        
#         instruction_set_node_answer_id = f"node-{str(uuid.uuid4())}"
#         label = f"Instruction Set "
#         print(socketio)
#         socketio.emit('update', {'id': instruction_set_node_answer_id, 'label': instruction_set,'parentId': instruction_set_node_id, 'type' : "displayNode"})
        
#         final_instruction_set = finetune_instruction_set(image_path + "_train_",image_path + "_numbered__train_",image_path, instruction_set,data_new)

#         instruction_finetune_node_id = f"node-{str(uuid.uuid4())}"
#         label = f"Finetuned Instruction Set "
#         print(socketio)
#         socketio.emit('update', {'id': instruction_finetune_node_id, 'label': label,'parentId': instruction_set_node_answer_id, 'type' : "textUpdater"})
        
#         instruction_finetune_node_answer_id = f"node-{str(uuid.uuid4())}"
#         label = f"Finetuned Instruction Set "
#         print(socketio)
#         socketio.emit('update', {'id': instruction_finetune_node_answer_id, 'label': final_instruction_set,'parentId': instruction_finetune_node_id, 'type' : "displayNode"})
        
#         final_output_test = generate_output(image_path, final_instruction_set, data_new)

#         raw_output_node_id = f"node-{str(uuid.uuid4())}"
#         label = f"Generate the exact output"
#         print(socketio)
#         socketio.emit('update', {'id': raw_output_node_id, 'label': label,'parentId': instruction_finetune_node_answer_id, 'type' : "textUpdater"})

#         raw_output_node_answer_id = f"node-{str(uuid.uuid4())}"
#         label = f"Raw Output"
#         print(socketio)
#         socketio.emit('update', {'id': raw_output_node_answer_id, 'label': final_output_test,'parentId': raw_output_node_id, 'type' : "displayNode"})
        
#         final_output_formatted = answer_formatting(final_output_test, output_format)

#         formatted_output_node_id = f"node-{str(uuid.uuid4())}"
#         label = f"Format the output correctly"
#         print(socketio)
#         socketio.emit('update', {'id': formatted_output_node_id, 'label': label,'parentId': raw_output_node_id, 'type' : "textUpdater"})
        
#         formatted_output_node_answer_id = f"node-{str(uuid.uuid4())}"
#         label = f"Formatted Output"
#         print(socketio)
#         socketio.emit('update', {'id': formatted_output_node_answer_id, 'label': final_output_formatted,'parentId': formatted_output_node_id, 'type' : "displayNode"})
        
#         print("The FINAL ANSWER is: ")
#         print(final_output_formatted.replace("```","").replace("json","").lower().replace("output:","").replace('"""',"").replace("'",""))
#         final_list = convert_to_2d_array(final_output_formatted.replace("```","").replace("json","").lower().replace("output:","").replace('"""',"").replace("'",""))
#         print("\n Actual answer is : ")
#         print(test_o)
#         answer_node_id = f"node-{str(uuid.uuid4())}"
#         label = f"Final Answer"
#         print(socketio)
#         socketio.emit('update', {'id': answer_node_id, 'label': final_list,'parentId': formatted_output_node_answer_id, 'type' : "displayNode"})
#         print("\n\nTHE VERDICT IS :\n\n")

#         if final_list == test_o:
#             return "The answer is correct!"
#         else:
#             return "The answer is incorrect"
#     else:
#         return "No test images found in the JSON file."
