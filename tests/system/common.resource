*** Settings ***
Documentation    Common keywords to run the command line tool system tests.
Library     Collections
Library     OperatingSystem
Library     Process
Library     String


*** Keywords ***
Run Process Check Output
    [Documentation]    Runs a process with the given command and arguments,
    ...    checks for successful execution and returns the result object.
    [Arguments]    @{cmd}    ${expected_rc}=0    ${env_extra}=${None}
    &{env} =    Get Environment Variables
    IF    ${env_extra} is not None
        VAR    &{env}    &{env}    &{env_extra}
    END
    ${res} =    Run Process    @{cmd}    env=${env}
    IF    ${res.rc} != ${expected_rc}
        ${cmdline} =    Join Command Line    @{cmd}
        ${error} =    Set Variable
        ...    Process failed with return code ${res.rc} (expecting ${expected_rc})
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

Normalize Output
    [Documentation]    Replaces non-deterministic parts of the output (like elapsed times)
    ...    with a fixed placeholder to make the output comparison robust.
    [Arguments]    ${output}
    # Normalize keyword elapsed times (e.g., "  ✓ PASS     0s")
    # We use 4 spaces to match the output format of RobotTrace.py
    ${output} =    Replace String Using Regexp    ${output}
    ...    (PASS|SKIP|FAIL|NOT RUN) {2,}\\d+h \\d+m \\d+s    \\1${SPACE}${SPACE}${SPACE}${SPACE}0s
    ${output} =    Replace String Using Regexp    ${output}
    ...    (PASS|SKIP|FAIL|NOT RUN) {2,}\\d+m \\d+s    \\1${SPACE}${SPACE}${SPACE}${SPACE}0s
    ${output} =    Replace String Using Regexp    ${output}
    ...    (PASS|SKIP|FAIL|NOT RUN) {2,}\\d+s    \\1${SPACE}${SPACE}${SPACE}${SPACE}0s
    # Normalize "Total elapsed:  0s."
    ${output} =    Replace String Using Regexp    ${output}
    ...    Total elapsed: {1,}\\d+h \\d+m \\d+s\\.    Total elapsed:${SPACE}${SPACE}0s.
    ${output} =    Replace String Using Regexp    ${output}
    ...    Total elapsed: {1,}\\d+m \\d+s\\.    Total elapsed:${SPACE}${SPACE}0s.
    ${output} =    Replace String Using Regexp    ${output}
    ...    Total elapsed: {1,}\\d+s\\.    Total elapsed:${SPACE}${SPACE}0s.
    RETURN    ${output}
