*** Settings ***
Suite Setup    Do Suite Setup


*** Test Cases ***
Passing Test Case
    Log    Simple test case


*** Keywords ***
Do Suite Setup
    Run Keyword And Ignore Error    Should Be Equal    1    1
    Run Keyword And Ignore Error    Should Be Equal    1    2
