*** Test Cases ***
Test That Calls Run Keyword And Ignore Error
    Log    Starting the testcase
    Run Keyword And Ignore Error    Should Be Equal    1    1
    Run Keyword And Ignore Error    Should Be Equal    1    2
    Log    Finishing the testcase
