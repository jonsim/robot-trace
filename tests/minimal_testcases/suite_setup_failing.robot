*** Settings ***
Suite Setup     Do Suite Setup


*** Test Cases ***
Test Case 1
    Log    In Test Case 1


*** Keywords ***
Do Suite Setup
    Log    Doing suite setup
    Fail    The keyword failed
