*** Settings ***
Suite Teardown      Do Suite Teardown


*** Test Cases ***
Test Case 1
    Log    In Test Case 1


*** Keywords ***
Do Suite Teardown
    Log    Doing suite teardown
    Fail    The keyword failed
