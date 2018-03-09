import requests
import json
import argparse
import time
from termcolor import colored
import collections
import os
import argparse

import yaml

with open("config.yml", 'r') as config:
    cfg = yaml.load(config)

user= cfg['api']['user']
key = cfg['api']['key']

headers = {"Content-Type":"application/json", "x-api-user": user, "x-api-key": key }

task_list = {}

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_tasks():
    tasks = requests.get("https://habitica.com/api/v3/tasks/user"+"?type="+args.tasktype,headers=headers).json()
    task_num = [0, 0, 0, 0]
    for task in tasks['data']:
        task_num[0] += 1
        task_list[task_num[0]] = task
    return task_list


def print_tasks():
    task_list = get_tasks()
    print "Your {0} tasks".format(args.tasktype)
    for num,task in task_list.items():
        if  not args.onlyactive or (args.onlyactive and not task['completed']) :
            if task['priority'] < 1:
                print colored(str(num) + " : " + task['text'], 'blue')
            if task['priority'] == 1:
                print colored(str(num) + " : " + task['text'], 'green')
            if task['priority'] == 1.5:
                print colored(str(num) + " : " + task['text'], 'yellow')
            if task['priority'] == 2:
                print colored(str(num) + " : " + task['text'], 'red')
    print ""

def mark_dailys():
    task_list = get_tasks()
    for i in args.taskid:
        taskid = task_list[int(i)]["_id"]
        print task_list[int(i)]['text'] + " | Success: " + str(requests.post("https://habitica.com/api/v3/tasks/"+taskid+"/score/up",headers=headers).json()["success"])

def mark_habits():
    task_list = get_tasks()

    for task in args.taskid:
        taskid = task_list[int(task)]["_id"]
        count = args.taskcount
        if task_list[int(task)]["up"] and task_list[int(task)]["down"]:
            quality = args.taskresult
        elif task_list[int(task)]["up"]:
            quality = "up"
        else:
            quality = "down"

        for times in range(count):
            success = False
            while not success:
                success = requests.post("https://habitica.com/api/v3/tasks/"+taskid+"/score/"+quality,headers=headers).json()["success"]
                print "Success: " + str(success)


def mark_tasks():
    if args.tasktype == "dailys":
        mark_dailys()
    if args.tasktype == "habits":
        mark_habits()
    else:
        task_list = get_tasks()
        for taskid in args.taskid:
            taskid = task_list[int(taskid)]["_id"]
            count = args.taskcount
            quality = args.taskresult

            for times in range(count):
                success = False
                while not success:
                    success = requests.post("https://habitica.com/api/v3/tasks/"+taskid+"/score/"+quality,headers=headers).json()["success"]
                    print "Success: " + str(success)


def get_actions():
    actions = {
               'list' : 'list tasks, args: $0 - taskType(default todos)',
               'mark': 'mark as done, args: $0 - taskType(default todos)',
               'clear': 'clear screen'
              }
    return actions

def print_action():
    actions = get_actions()
    actions = collections.OrderedDict(sorted(actions.items()))
    print "Menu:"
    for action_num, action in actions.items():
        print colored(action_num, 'green') + " : " + colored(action, 'red')

def clear_screen(*action_args):
    os.system('clear')

def action_selector():
    actions = {
               'list' : print_tasks,
               'mark' : mark_tasks,
               'clear' : clear_screen,
               'help': print_action,
              }

    return (actions[args.action])()

def main_menu():
        action_selector()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to use habitica from cmdline')
    parser.add_argument('--action', '-A', help='actions that you can perform',required=True)
    parser.add_argument('--tasktype', '-T', default="habits",help='task type that should be considered',required=False)
    parser.add_argument('--taskid', '-TID', nargs='*', type=int  ,help='task type that should be considered',required=False)
    parser.add_argument('--taskcount', '-TC', type=int ,help='task type that should be considered',required=False)
    parser.add_argument('--taskresult', '-TR' ,help='task type that should be considered',required=False)
    parser.add_argument('--onlyactive',  type=str2bool, default=False, help='task type that should be considered',required=False)

    args = parser.parse_args()

    main_menu()
