*** Test Cases ***
Test Case 1
    Log    In Test Case 1
    [Teardown]    Do Test Teardown


*** Keywords ***
Do Test Teardown
    Log    Doing test teardown
    ${value}=    Evaluate    1 + 2
    Should Be Equal As Numbers    ${value}    3
    Log    Test teardown completed    level=WARN
