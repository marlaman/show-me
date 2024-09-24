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

os.environ["OPENAI_API_KEY"] = 'sk-proj-mtnt5y5G2U2DhczZUg6DT3BlbkFJNiSb59Zvu7ipGJ3R1anS'
           
llm = ChatOpenAI(model='gpt-4o-mini',temperature = 00)

LANGCHAIN_TRACING_V2=True
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="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"
LANGCHAIN_PROJECT="pr-plaintive-succotash-73"



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

        Your one and only goal is to determine if the task in hand is meant for multi-step reasoning or can be answered immediately using the infornation

        Here are some tips that will help you make a decision:
        
        1) Always return False if it's the main task, unless its very very obvious trivia type of question
        2) If it's not the main task, you should really be conservative in splitting it(returning False) unless you really think splitting it would give added benefits. So most times you'll end up returning True, unless obviosly its the main task, then you mostly return False
        
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
        ("system", """You will be given a question. Assumming that there has been an answer generated for the question, what are the smallest number of checks
        we can have in place to make sure that the answer exactly answers the question given?

        Assume that any source of information used to retrieve the information is accurate, no need to ask for sources too.

        MAKE SURE EVERY CHECK IS UNIQUE AND THAT ONE CHECK NEVER DOES WHAT ANY OTHER CHECK DOES
        
        Return a numbered list of these checks in the form of questions that ensure that the question has been answered in a logical way

      
        Example  
        
        Input - What is the answer to this `example-puzzle with condition 1,2,3`?

        OUtput - 1) Does the answer meet the condition 1?
                2) Does the answer meet the condition 2?
                3) Does the answer meet the condition 3?

        (IT DOESN'T HAVE TO BE 3 CONDITIONS. ONLY THE MINIMUM NUMBER OF CONDITIONS TO TEST THE ANSWER PLEASE.)        
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
        ("system", """You will be given a software development task and the tests to check the answer.

        Your task is to return the smallest number of tasks to do to answer the question, keeping in mind the tests.

        Here is the key instruction - 

        NO SUB-TASK SHOULD EVER BE ABOUT CHECKING ANYTHING. CHECKING WILL BE DONE IN A LATER STAGE ANYWAY.

        MAKE SURE THAT THE TASKS ARE CLEAR AND INSTRUCTIVE Step-by-step manner AND NEVER EVER VAGUE. A HUMAN MUST BE ABLE TO ANSWER EACH TASK CLEARLY in order to get the answer. DO NOT USE WORDS LIKE ANALYZE, OBSERVE, EXPLAIN, CONFIRM. YOU WORDS LIKE 'D0','DETERMINE'. THE TASKS MUST BE ABLE TO BE PERFORMED BY AN IDIOT TOO. 

        Example 1 - 

        Input - What is the alternative name of the capital of the biggest state in India?

        Output - 1) Determine the largest state in India
                2) Determine the capital of the largest state in India
                3) Determine the alternative name of the capital city

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

def task_rru_software(task,socketio, previous_answers="No Previous Answers", main_task_context="This is the main task", node_id=None, parent_node_id = None):

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
        # If the task is not split, perform the task and return it
        task_answer = perform_task(task, previous_answers, main_task_context)
        return task_answer
    else:
        if parent_node_id:
            socketio.emit('update', {'id': description_node_id, 'label': label,'parentId': parent_node_id, 'type' : "subTask", 'hasTests': True})
        else:
            socketio.emit('update', {'id': description_node_id, 'label': label,'parentId': parent_node_id, 'type' : "mainTask", 'hasTests': True})
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
            temp_answer = task_rru_software(current, socketio, full_answer, mt_context, sub_task_id,description_node_id)
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
