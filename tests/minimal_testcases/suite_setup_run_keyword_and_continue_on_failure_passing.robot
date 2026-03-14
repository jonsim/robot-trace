*** Settings ***
Suite Setup    Do Suite Setup


*** Test Cases ***
Empty Test Case
    Log    Simple test case


*** Keywords ***
Do Suite Setup
    Run Keyword And Continue On Failure    Should Be Equal    1    1
