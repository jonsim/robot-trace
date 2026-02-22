*** Test Cases ***
Passing Testcase
    Log    Starting the passing testcase
    ${value}=    Evaluate    1 + 2
    Should Be Equal As Numbers    ${value}    3
    Log    Passing testcase completed
