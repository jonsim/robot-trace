*** Settings ***
Suite Teardown      Do Suite Teardown


*** Test Cases ***
Test Case 1
    Log    In Test Case 1
    Skip    Skip the testcase


*** Keywords ***
Do Suite Teardown
    Log    Doing suite teardown
    Fail    But then fail the suite teardown
