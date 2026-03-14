*** Settings ***
Suite Teardown    Do Suite Teardown


*** Test Cases ***
Empty Test Case
    Log    Simple test case


*** Keywords ***
Do Suite Teardown
    Run Keyword And Continue On Failure    Should Be Equal    1    2
