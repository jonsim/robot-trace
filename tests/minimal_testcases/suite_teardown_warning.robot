*** Settings ***
Suite Teardown      Do Suite Teardown


*** Test Cases ***
Test Case 1
    Log    In Test Case 1


*** Keywords ***
Do Suite Teardown
    Log    Doing suite teardown
    ${value}=    Evaluate    1 + 2
    Should Be Equal As Numbers    ${value}    3
    Log    Suite teardown completed    level=WARN
