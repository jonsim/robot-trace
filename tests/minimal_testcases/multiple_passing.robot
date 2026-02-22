*** Test Cases ***
Passing Testcase 1
    Log    Starting the first passing testcase
    Should Be Equal    ${True}    ${True}
    Log    First passing testcase completed

Passing Testcase 2
    Log    Starting the second passing testcase
    Should Be Equal    ${False}    ${False}
    Log    Second passing testcase completed
