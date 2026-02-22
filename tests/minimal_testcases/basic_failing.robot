*** Test Cases ***
Failing Testcase
    Log    Starting the failing testcase
    ${value}=    Evaluate    1 + 2
    Should Be Equal As Numbers    ${value}    4
    Log    Unreachable line
