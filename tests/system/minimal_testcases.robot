*** Settings ***
Documentation     Runs each of the minimal testcases in ../minimal_testcases and
...    checks the output matches.
Library           Collections
Library           OperatingSystem
Library           String
Resource          common.resource
Test Template     Run Minimal Testcase
Suite Setup       Set Robot Version


*** Variables ***
${TESTCASE_DIR}    ${CURDIR}${/}..${/}minimal_testcases


*** Test Cases ***                              TESTCASE                            OPTIONS
# robocop: off=NAME07  It's useful to have the test case names match the file.
basic_failing                                   basic_failing
basic_failing (verbose)                         basic_failing                       mode=verbose
basic_passing                                   basic_passing
basic_passing (verbose)                         basic_passing                       mode=verbose
basic_skipping                                  basic_skipping
basic_skipping (verbose)                        basic_skipping                      mode=verbose
for_failing                                     for_failing
for_failing (verbose)                           for_failing                         mode=verbose
for_passing                                     for_passing
for_passing (verbose)                           for_passing                         mode=verbose
if_else_failing                                 if_else_failing
if_else_failing (verbose)                       if_else_failing                     mode=verbose
if_else_passing                                 if_else_passing
if_else_passing (verbose)                       if_else_passing                     mode=verbose
invalid_syntax                                  invalid_syntax                      expected_rc=1
invalid_syntax (verbose)                        invalid_syntax                      expected_rc=1       mode=verbose
log_debug                                       log_debug                           -LDEBUG
log_debug (verbose)                             log_debug                           -LDEBUG             mode=verbose
log_error                                       log_error
log_error (verbose)                             log_error                           mode=verbose
log_multiline                                   log_multiline
log_multiline (verbose)                         log_multiline                       mode=verbose
log_warning                                     log_warning
log_warning (verbose)                           log_warning                         mode=verbose
multiple_2failing                               multiple_2failing
multiple_2failing (verbose)                     multiple_2failing                   mode=verbose
multiple_passing                                multiple_passing
multiple_passing (verbose)                      multiple_passing                    mode=verbose
nested_keywords_1                               nested_keywords_1
nested_keywords_1 (verbose)                     nested_keywords_1                   mode=verbose
nested_keywords_2                               nested_keywords_2
nested_keywords_2 (verbose)                     nested_keywords_2                   mode=verbose
nested_keywords_3                               nested_keywords_3
nested_keywords_3 (verbose)                     nested_keywords_3                   mode=verbose
nested_keywords_failing                         nested_keywords_failing
nested_keywords_failing (verbose)               nested_keywords_failing             mode=verbose
run_keywords_failing                            run_keywords_failing
run_keywords_failing (verbose)                  run_keywords_failing                mode=verbose
run_keywords_passing                            run_keywords_passing
run_keywords_passing (verbose)                  run_keywords_passing                mode=verbose
suite_setup_failing                             suite_setup_failing
suite_setup_failing (verbose)                   suite_setup_failing                 mode=verbose
suite_setup_failing_testcase                    suite_setup_failing_testcase
suite_setup_failing_testcase (verbose)          suite_setup_failing_testcase        mode=verbose
suite_setup_passing                             suite_setup_passing
suite_setup_passing (verbose)                   suite_setup_passing                 mode=verbose
suite_setup_warning                             suite_setup_warning
suite_setup_warning (verbose)                   suite_setup_warning                 mode=verbose
suite_teardown_failing                          suite_teardown_failing
suite_teardown_failing (verbose)                suite_teardown_failing              mode=verbose
suite_teardown_failing_testcase                 suite_teardown_failing_testcase
suite_teardown_failing_testcase (verbose)       suite_teardown_failing_testcase     mode=verbose
suite_teardown_passing                          suite_teardown_passing
suite_teardown_passing (verbose)                suite_teardown_passing              mode=verbose
suite_teardown_warning                          suite_teardown_warning
suite_teardown_warning (verbose)                suite_teardown_warning              mode=verbose
test_setup_failing                              test_setup_failing
test_setup_failing (verbose)                    test_setup_failing                  mode=verbose
test_setup_passing                              test_setup_passing
test_setup_passing (verbose)                    test_setup_passing                  mode=verbose
test_setup_warning                              test_setup_warning
test_setup_warning (verbose)                    test_setup_warning                  mode=verbose
test_teardown_failing                           test_teardown_failing
test_teardown_failing (verbose)                 test_teardown_failing               mode=verbose
test_teardown_passing                           test_teardown_passing
test_teardown_passing (verbose)                 test_teardown_passing               mode=verbose
test_teardown_warning                           test_teardown_warning
test_teardown_warning (verbose)                 test_teardown_warning               mode=verbose
try_catch_exception                             try_catch_exception
try_catch_exception (verbose)                   try_catch_exception                 mode=verbose
try_catch_passing                               try_catch_passing
try_catch_passing (verbose)                     try_catch_passing                   mode=verbose


*** Keywords ***
Run Minimal Testcase
    [Documentation]    Runs one of the minimal testcases and checks that the
    ...    output matches.
    [Arguments]    ${testcase}    @{additional_args}    ${mode}=normal    ${expected_rc}=0
    ${testcase_file} =    Set Variable    ${TESTCASE_DIR}${/}${testcase}.robot
    ${testcase_result} =    Set Variable    ${TESTCASE_DIR}${/}${testcase}.trace.${mode}
    IF    ${ROBOT_VERSION_MAJOR} < 7
        IF    os.path.exists("${TESTCASE_DIR}${/}${testcase}.trace.rf6.${mode}")
            ${testcase_result} =    Set Variable    ${TESTCASE_DIR}${/}${testcase}.trace.rf6.${mode}
        END
    END
    IF    "failing" in "${testcase}" and ${expected_rc} == 0
        ${match} =    Evaluate    re.search(r"(\\d+)failing", "${testcase}")
        ${expected_rc} =    Set Variable    ${{$match.group(1) if $match else 1}}
    END
    IF    "${mode}" == "verbose"
        Append To List    ${additional_args}    --verbose
    END
    File Should Exist    ${testcase_file}
    File Should Exist    ${testcase_result}
    ${res} =  Run Process Check Output
    ...    robot-trace
    ...    --output      NONE
    ...    --report      NONE
    ...    --log         NONE
    ...    @{additional_args}
    ...    ${testcase_file}
    ...    expected_rc=${expected_rc}
    Should Be Equal    ${EMPTY}    ${res.stderr}
    ${testcase_expectation} =    Get File    ${testcase_result}
    ${testcase_expectation} =    Strip String    ${testcase_expectation}
    Should Be Equal    ${testcase_expectation}    ${res.stdout}
