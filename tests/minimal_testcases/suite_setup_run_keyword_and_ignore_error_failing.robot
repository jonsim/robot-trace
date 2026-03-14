*** Settings ***
Suite Setup    Do Suite Setup


*** Test Cases ***
Failing Test Case
    Fail    Always fails


*** Keywords ***
Do Suite Setup
    Run Keyword And Ignore Error    Should Be Equal    1    1
    Run Keyword And Ignore Error    Should Be Equal    1    2
