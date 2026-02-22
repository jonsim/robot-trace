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
        ${error} =    Set Variable
        ...    Process failed with return code ${res.rc}
        ...    \n\nCommand:\n${cmdline}
        ...    \n\nStandard Output:\n${res.stdout}
        ...    \n\nStandard Error:\n${res.stderr}
        Fail    ${error}
    END
    RETURN    ${res}

Set Robot Version
    [Documentation]    Returns the version of Robot Framework being used.
    ${res} =    Run Process    robot    --version
    ${version} =    Remove String Using Regexp    ${res.stdout}
    ...    [Rr]obot ?[Ff]ramework
    ...    \\(.*\\)
    ${version} =    Strip String    ${version}
    ${major} =    Convert To Integer    ${{"${version}".split(".")[0]}}
    ${minor} =    Convert To Integer    ${{"${version}".split(".")[1]}}
    Set Suite Variable    ${ROBOT_VERSION}    ${version}
    Set Suite Variable    ${ROBOT_VERSION_MAJOR}    ${major}
    Set Suite Variable    ${ROBOT_VERSION_MINOR}    ${minor}
