*** Test Cases ***
Test Case 1
    [Setup]    Do Test Setup
    Log    In Test Case 1


*** Keywords ***
Do Test Setup
    Log    Doing test setup
    ${value}=    Evaluate    1 + 2
    Should Be Equal As Numbers    ${value}    3
    Log    Test setup completed
