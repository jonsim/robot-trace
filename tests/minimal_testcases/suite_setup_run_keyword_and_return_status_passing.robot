*** Settings ***
Suite Setup    Do Suite Setup


*** Test Cases ***
Passing Test Case
    Log    Simple test case


*** Keywords ***
Do Suite Setup
    ${status} =    Run Keyword And Return Status    Should Be Equal    1    1
    Log    Returned status: ${status}
    ${status} =    Run Keyword And Return Status    Should Be Equal    1    2
    Log    Returned status: ${status}
