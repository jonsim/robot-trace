*** Test Cases ***
Test That Calls Run Keyword And Continue On Failure
    Log    Starting the testcase
    Run Keyword And Continue On Failure    Fail    Always fails
    Log    Finishing the testcase
