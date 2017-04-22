# Author: Sungchul Choi, sc82.choi AT gachon.ac.kr
# Version: 0.0.3
# Description
# 가천대학교 CS50 수업에 활용되는 "숙제 자동 채점 프로그램"의 Client 프로그램입니다.
# This is a program to automatically grade a submitted code for Gachon CS50 Classes.
# Copyright (C) 2015 TeamLab@Gachon University
# Email: teamlab.gachon AT gmail.com
# HUMAN KNOWLEDGE BELONGS TO THE WORLD. -- From the movie "Antitrust"

import argparse
import pickle
import os
import types
import requests
import json

import sys

TOKEN_PICKLE_FILE_NAME = "access_token"
HOST = "theteamlab.io"

def set_host_address(host_name):
    global HOST
    HOST = host_name

def getArgumentsParser(argv=None):
    parser = argparse.ArgumentParser(
        prog='An program for autograder of your assignement. Coded by TeamLab@Gachon University ',)
    parser.add_argument("-get", help="Write your assignment name that you want to download")
    parser.add_argument("-submit", help="Write your assignment name that you want to submit")
    argumentValue = parser.parse_args(argv)

    if not (argumentValue.get or argumentValue.submit):
        parser.error('One of -submit or -get must be given')

    return argumentValue;


def checkArguements(argumentValue):
    if argumentValue.get != None:
        return ["get", argumentValue.get]
    if argumentValue.submit != None:
        return ["submit", argumentValue.submit]
    return ["error", "error"]


def printInformationMessage(actionType, assignmentName):
    if (actionType == "get"):
        message = "== Getting templates | "
    else:
        message = "== Submmting solutions | "
    sys.stdout.write  (message + assignmentName + "\n")

# Get JWT token to access REST API
def getToken():
    if os.path.isfile(TOKEN_PICKLE_FILE_NAME):
        try:
            with open(TOKEN_PICKLE_FILE_NAME, 'rb') as accesstoken:
                token_file = pickle.load(accesstoken)
                return token_file['token'], token_file['username']
        except EOFError:
            sys.stdout.write  ("Existing access_token is NOT validated"+ "\n")
            return None, None
    else:
        return None,None


def getLoginInformation():
    login_id = input("Login ID: ")
    login_password = input("Password :")
    return [login_id, login_password]


def getAccessTokenFromServer(username, login_password):
    headers = {'Content-type': 'application/json'}
    payload = {"password":login_password, "username":username}

    access_token_jwt = requests.post("http://"+HOST+"/api-token-auth/", json=payload, headers=headers)


    if (access_token_jwt.ok) : return access_token_jwt.text
    else: return None

def makeAccessTokenPickle(access_token, username):
    pickle_file_Name = "access_token"
    pcikleObject = open(pickle_file_Name,'wb')
    username_json = {'username' : username}
    toekn_json = {'token' : access_token}
    data =json.loads(json.dumps(toekn_json , ensure_ascii=False))
    data.update(username_json)
    pickle.dump(data, pcikleObject)
    return pickle

def checkTokenReplacement(username):
    replacment = 'a'
    while replacment.lower() not in ['t','yes','y','true', 'n','no','f','false']:
        message = ("Use token from last successful submission (%s)? (Y/n): " % username)
        replacment = input(message)
        if replacment.lower() in ['t','yes','y','true']:
            return True
        elif replacment.lower() in ['n','no','f','false']:
            return False
        else:
            sys.stdout.write  ("Wrong Input"+ "\n")

    return True

def getFileContents(fileName):
    with open (fileName, "r", encoding="utf-8") as contens_file:
        contens = contens_file.read()
    return contens


def getAssignmentTemplateFileFromServer(access_token, assignment_name):
    payload = {
            "assignment_name" : assignment_name,
       }

    accesstoken_dict = json.loads(access_token)
    headers = {'Authorization': 'JWT ' + accesstoken_dict['token']}
    result = requests.post("http://"+HOST+"/autograder/assignments/%s/submissionready" % assignment_name, json=payload, headers=headers)
    return result

def submitAssignmentFileToServer(access_token, assignment_file_name):

    assignment_contents = getFileContents(assignment_file_name)

    [basename, ext] = assignment_file_name.split(".")

    payload = {
            "template_file_name" : assignment_file_name,
            "template_file_contents" : assignment_contents,
    }

    accesstoken_dict = json.loads(access_token)
    headers = {'Authorization': 'JWT ' + accesstoken_dict['token']}
    result = requests.post("http://"+HOST+"/autograder/assignments/%s/submission" % basename, json=payload, headers=headers)

    #TODO Add exception handling

    return result

def makeTemplateFile(result_text):
    try:
        data = json.loads(result_text, strict=False)
        with open(data['template_file_name'], 'w', encoding='utf-8') as f:
            print(type(data['template_file_contents']))
            f.write(data['template_file_contents'])
            sys.stdout.write  ("%s file is created for your %s assignment \n" % (data['template_file_name'], data['assignment_name']))
        return True
    except IOError:
        sys.stdout.write  ("Unavailable making the template file: %s \n" % data['template_file_name'])
        return False
    except TypeError:
        sys.stdout.write  ("Unexpected Error occured")
        return False


def removeExpiredAccessKey():
    if os.path.isfile(TOKEN_PICKLE_FILE_NAME):
        os.remove(TOKEN_PICKLE_FILE_NAME)
    else:    ## Show an error ##
        sys.stdout.write ("Error: %s file not found \n" % TOKEN_PICKLE_FILE_NAME)

def printTestResults(text):
    json_data = json.loads(text)

    a = "-"*20; b = "-"*10; c = "-"*20
    sys.stdout.write  ( '%20s | %10s | %20s \n' % (a,b,c) )
    sys.stdout.write  ( '%20s | %10s | %20s \n' % ("Function Name","Passed?","Feedback") )
    sys.stdout.write  ( '%20s | %10s | %20s \n' % (a,b,c) )

    for result in json_data:
        if result['test_result'] == ('S'):
            passed = 'PASS'
            feedback = 'Good Job'
        else:
            passed = 'Not Yet'
            if result['test_result'] == ('E'):
                feedback = 'Check Your Logic'
            if result['test_result'] == ('F'):
                feedback = 'Check Your Grammar'
        sys.stdout.write  ( '%20s | %10s | %20s \n' % (result['assignment_detail'],passed,feedback ) )

    sys.stdout.write  ( '%20s | %10s | %20s \n' % (a,b,c) )

def get_assignment(username, password, assignment_name, host_name=None):
    if host_name is not None:
        set_host_address(host_name)
    access_token = getAccessTokenFromServer(username, password)
    makeAccessTokenPickle(access_token, username)

    result = getAssignmentTemplateFileFromServer(access_token, assignment_name)
    if (result.status_code == 200):
        is_file_created = makeTemplateFile(result.text)
        if (is_file_created == True):
            sys.stdout.write ("Thank you for using the program. Enjoy Your Assignment - From TeamLab \n")
    elif (result.status_code == 403):
        sys.stdout.write  (result.text + "\n")
        removeExpiredAccessKey()
        sys.stdout.write  ("Your expired access key removed. Please, try again \n")
    elif (result.status_code == 500):
        sys.stdout.write  (result.text + "\n")
        sys.stdout.write  ("Unexpected error exists. Please contact teamlab.gachon@gmail.com \n")


def submit_assignment(username, password, assignment_name, host_name=None):
    if host_name is not None:
        set_host_address(host_name)
    access_token = getAccessTokenFromServer(username, password)
    makeAccessTokenPickle(access_token, username)

    result = submitAssignmentFileToServer(access_token, assignment_name)
    if (result.status_code == 200):
        printTestResults(result.text)
        # Make access pickle before end of program
    elif (result.status_code == 403):
        sys.stdout.write  (result.text +"\n")
        removeExpiredAccessKey()
        sys.stdout.write  ("Your expired access key removed. Please, try again \n")
    elif (result.status_code == 500):
        sys.stdout.write  ("Unexpected error exists. Maybe you need to debuge \n")
        sys.stdout.write  ("Unexpected error exists. Please contact teamlab.gachon@gmail.com \n")



def main():

    # Get arguements
    argumentValue = getArgumentsParser()

    # Check Argument
    # To download an assignment template file : -get <ASSIGNMENT_NAME>
    # To submit an assignment template file : -submit <ASSIGNMENT_NAME>
    [actionType, assignment_name] = checkArguements(argumentValue)

    # Check User Login Information
    printInformationMessage(actionType, assignment_name)

    # Check Your Access Token
    [access_token, username]  = getToken()

    # Get New Access Token
    if access_token == None:
        while (access_token == None):
            [username, login_password] = getLoginInformation()
            access_token = getAccessTokenFromServer(username, login_password)
            if (access_token == None): sys.stdout.write  ("Wrong username or password. Please, input again. \n")
    else:
        answer = checkTokenReplacement(username)
        if (answer == False):
            access_token = None
        while (access_token == None):
            [username, login_password] = getLoginInformation()
            access_token = getAccessTokenFromServer(username, login_password)
            if (access_token == None): sys.stdout.write  ("Wrong username or password. Please, input again. \n")

    # Make access pickle before end of program
    makeAccessTokenPickle(access_token, username)

    if (actionType == "get"):
        result = getAssignmentTemplateFileFromServer(access_token, assignment_name)
        if (result.status_code == 200):
            is_file_created = makeTemplateFile(result.text)
            if (is_file_created == True):
                sys.stdout.write ("Thank you for using the program. Enjoy Your Assignment - From TeamLab \n")
        elif (result.status_code == 403):
            sys.stdout.write  (result.text + "\n")
            removeExpiredAccessKey()
            sys.stdout.write  ("Your expired access key removed. Please, try again \n")
        elif (result.status_code == 500):
            sys.stdout.write  (result.text + "\n")
            sys.stdout.write  ("Unexpected error exists. Please contact teamlab.gachon@gmail.com \n")

    elif (actionType == "submit"):
        result = submitAssignmentFileToServer(access_token, assignment_name)
        if (result.status_code == 200):
            printTestResults(result.text)
            # Make access pickle before end of program
        elif (result.status_code == 403):
            sys.stdout.write  (result.text +"\n")
            removeExpiredAccessKey()
            sys.stdout.write  ("Your expired access key removed. Please, try again \n")
        elif (result.status_code == 500):
            sys.stdout.write  ("Unexpected error exists. Please contact teamlab.gachon@gmail.com \n")

if __name__ == "__main__":
    main()