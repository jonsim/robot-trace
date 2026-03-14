*** Settings ***
Suite Teardown    Do Suite Teardown


*** Test Cases ***
Passing Test Case
    Log    Simple test case


*** Keywords ***
Do Suite Teardown
    ${status} =    Run Keyword And Return Status    Should Be Equal    1    1
    Log    Returned status: ${status}
    ${status} =    Run Keyword And Return Status    Should Be Equal    1    2
    Log    Returned status: ${status}
