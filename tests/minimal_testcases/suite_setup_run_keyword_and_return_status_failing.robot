*** Settings ***
Suite Setup    Do Suite Setup


*** Test Cases ***
Failing Test Case
    Fail    Always fails


*** Keywords ***
Do Suite Setup
    ${status} =    Run Keyword And Return Status    Should Be Equal    1    1
    Log    Returned status: ${status}
    ${status} =    Run Keyword And Return Status    Should Be Equal    1    2
    Log    Returned status: ${status}
