*** Settings ***
Suite Setup     Do Suite Setup


*** Test Cases ***
Test Case 1
    Log    In Test Case 1
    Fail    Test case always fails


*** Keywords ***
Do Suite Setup
    Log    Doing suite setup
    ${value}=    Evaluate    1 + 2
    Should Be Equal As Numbers    ${value}    3
    Log    Suite setup completed
