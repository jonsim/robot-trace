*** Settings ***
Suite Teardown    Do Suite Teardown


*** Test Cases ***
Failing Test Case
    Fail    Always fails


*** Keywords ***
Do Suite Teardown
    Run Keyword And Ignore Error    Should Be Equal    1    1
    Run Keyword And Ignore Error    Should Be Equal    1    2
