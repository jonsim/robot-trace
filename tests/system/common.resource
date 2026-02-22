*** Settings ***
Documentation    Common keywords to run the command line tool system tests.
Library     OperatingSystem
Library     Process
Library     String


*** Variables ***
${TESTCASE_DIR}     ${TEMPDIR}${/}robot-cli-testcases


*** Keywords ***
Run Process Check Output
    [Documentation]    Runs a process with the given command and arguments,
    ...    checks for successful execution and returns the result object.
    [Arguments]    @{cmd}    ${expected_rc}=0
    ${res} =    Run Process    @{cmd}
    IF    ${res.rc} != ${expected_rc}
        ${cmdline} =    Join Command Line    @{cmd}
        VAR    ${error} =
        ...    Process failed with return code ${res.rc}
        ...    \n\nCommand:\n${cmdline}
        ...    \n\nStandard Output:\n${res.stdout}
        ...    \n\nStandard Error:\n${res.stderr}
        Fail    ${error}
    END
    RETURN    ${res}
