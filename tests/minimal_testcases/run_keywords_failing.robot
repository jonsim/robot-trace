*** Test Cases ***
Test That Calls Run Keywords
    Log    Starting the testcase
    Run Keywords    Log    First keyword
    ...    AND
    ...    Fail    Explicit fail statement
    Log    Unreachable line
