*** Test Cases ***
Test That Calls Run Keyword And Ignore Error
    Log    Starting the testcase
    ${status} =    Run Keyword And Return Status    Should Be Equal    1    1
    Log    Returned status: ${status}
    ${status} =    Run Keyword And Return Status    Should Be Equal    1    2
    Log    Returned status: ${status}
