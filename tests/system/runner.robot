*** Settings ***
Documentation     Checks the behaviour of the robot-cli runner.
Library           OperatingSystem
Library           String
Resource          common.resource


*** Test Cases ***
Errors are reported correctly
    [Documentation]    Assert that errors from robot are correctly propagated
    ...    by the runner.
    ${expected_stderr} =    Catenate    SEPARATOR=\n
    ...    [ ERROR ] option --invalidargumentname not recognized
    ...
    ...    Try --help for usage information.
    ${res} =  Run Process Check Output
    ...    robot-cli
    ...    --output      NONE
    ...    --report      NONE
    ...    --log         NONE
    ...    --invalid-argument-name
    ...    expected_rc=252
    Should Be Equal    ${res.stderr}    ${expected_stderr}
    Should Be Equal    ${res.stdout}    ${EMPTY}
