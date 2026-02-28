*** Test Cases ***
Failing Testcase 1
    Log    Starting the first failing testcase
    Fail    This testcase failed
    Log    Unreachable line

Failing Testcase 2
    Log    Starting the second failing testcase
    Should Be Equal    ${False}    ${True}
    Log    Unreachable line
