# robocop: off=NAME07  It's useful to have the test case names match the file.
# robocop: off=LEN08   A few long lines - not ideal but better than splitting them.
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


*** Test Cases ***                                                          TESTCASE                                                        OPTIONS
basic_failing                                                               basic_failing
basic_failing (verbose)                                                     basic_failing                                                   mode=verbose
basic_failing (buffered)                                                    basic_failing                                                   mode=buffered
basic_passing                                                               basic_passing
basic_passing (verbose)                                                     basic_passing                                                   mode=verbose
basic_passing (buffered)                                                    basic_passing                                                   mode=buffered
basic_skipping                                                              basic_skipping
basic_skipping (verbose)                                                    basic_skipping                                                  mode=verbose
basic_skipping (buffered)                                                   basic_skipping                                                  mode=buffered
for_failing                                                                 for_failing
for_failing (verbose)                                                       for_failing                                                     mode=verbose
for_failing (buffered)                                                      for_failing                                                     mode=buffered
for_passing                                                                 for_passing
for_passing (verbose)                                                       for_passing                                                     mode=verbose
for_passing (buffered)                                                      for_passing                                                     mode=buffered
for_multiple_assignment                                                     for_multiple_assignment
for_multiple_assignment (verbose)                                           for_multiple_assignment                                         mode=verbose
for_multiple_assignment (buffered)                                          for_multiple_assignment                                         mode=buffered
for_continue                                                                for_continue
for_continue (verbose)                                                      for_continue                                                    mode=verbose
for_continue (buffered)                                                     for_continue                                                    mode=buffered
for_break                                                                   for_break
for_break (verbose)                                                         for_break                                                       mode=verbose
for_break (buffered)                                                        for_break                                                       mode=buffered
group_failing                                                               group_failing
group_failing (verbose)                                                     group_failing                                                   mode=verbose
group_passing                                                               group_passing
group_passing (verbose)                                                     group_passing                                                   mode=verbose
if_else_failing                                                             if_else_failing
if_else_failing (verbose)                                                   if_else_failing                                                 mode=verbose
if_else_failing (buffered)                                                  if_else_failing                                                 mode=buffered
if_else_passing                                                             if_else_passing
if_else_passing (verbose)                                                   if_else_passing                                                 mode=verbose
if_else_passing (buffered)                                                  if_else_passing                                                 mode=buffered
invalid_syntax                                                              invalid_syntax                                                  expected_rc=1
invalid_syntax (verbose)                                                    invalid_syntax                                                  expected_rc=1           mode=verbose
invalid_syntax (buffered)                                                   invalid_syntax                                                  expected_rc=1           mode=buffered
log_console                                                                 log_console
log_console (verbose)                                                       log_console                                                     mode=verbose
log_console (buffered)                                                      log_console                                                     mode=buffered
log_debug                                                                   log_debug                                                       -LDEBUG
log_debug (verbose)                                                         log_debug                                                       -LDEBUG                 mode=verbose
log_debug (buffered)                                                        log_debug                                                       -LDEBUG                 mode=buffered
log_error                                                                   log_error
log_error (verbose)                                                         log_error                                                       mode=verbose
log_error (buffered)                                                        log_error                                                       mode=buffered
log_multiline                                                               log_multiline
log_multiline (verbose)                                                     log_multiline                                                   mode=verbose
log_multiline (buffered)                                                    log_multiline                                                   mode=buffered
log_warning                                                                 log_warning
log_warning (verbose)                                                       log_warning                                                     mode=verbose
log_warning (buffered)                                                      log_warning                                                     mode=buffered
multiple_2failing                                                           multiple_2failing
multiple_2failing (verbose)                                                 multiple_2failing                                               mode=verbose
multiple_2failing (buffered)                                                multiple_2failing                                               mode=buffered
multiple_passing                                                            multiple_passing
multiple_passing (verbose)                                                  multiple_passing                                                mode=verbose
multiple_passing (buffered)                                                 multiple_passing                                                mode=buffered
nested_group_failing                                                        nested_group_failing
nested_group_failing (verbose)                                              nested_group_failing                                            mode=verbose
nested_group_failing (buffered)                                             nested_group_failing                                            mode=buffered
nested_group_passing                                                        nested_group_passing
nested_group_passing (verbose)                                              nested_group_passing                                            mode=verbose
nested_group_passing (buffered)                                             nested_group_passing                                            mode=buffered
nested_keywords_1                                                           nested_keywords_1
nested_keywords_1 (verbose)                                                 nested_keywords_1                                               mode=verbose
nested_keywords_1 (buffered)                                                nested_keywords_1                                               mode=buffered
nested_keywords_2                                                           nested_keywords_2
nested_keywords_2 (verbose)                                                 nested_keywords_2                                               mode=verbose
nested_keywords_2 (buffered)                                                nested_keywords_2                                               mode=buffered
nested_keywords_3                                                           nested_keywords_3
nested_keywords_3 (verbose)                                                 nested_keywords_3                                               mode=verbose
nested_keywords_3 (buffered)                                                nested_keywords_3                                               mode=buffered
nested_keywords_failing                                                     nested_keywords_failing
nested_keywords_failing (verbose)                                           nested_keywords_failing                                         mode=verbose
nested_keywords_failing (buffered)                                          nested_keywords_failing                                         mode=buffered
return_multiple_assignment                                                  return_multiple_assignment
return_multiple_assignment (verbose)                                        return_multiple_assignment                                      mode=verbose
return_multiple_assignment (buffered)                                       return_multiple_assignment                                      mode=buffered
run_keyword_and_continue_on_failure_failing                                 run_keyword_and_continue_on_failure_failing
run_keyword_and_continue_on_failure_failing (verbose)                       run_keyword_and_continue_on_failure_failing                     mode=verbose
run_keyword_and_continue_on_failure_failing (buffered)                      run_keyword_and_continue_on_failure_failing                     mode=buffered
run_keyword_and_continue_on_failure_passing                                 run_keyword_and_continue_on_failure_passing
run_keyword_and_continue_on_failure_passing (verbose)                       run_keyword_and_continue_on_failure_passing                     mode=verbose
run_keyword_and_continue_on_failure_passing (buffered)                      run_keyword_and_continue_on_failure_passing                     mode=buffered
run_keyword_and_ignore_error                                                run_keyword_and_ignore_error
run_keyword_and_ignore_error (verbose)                                      run_keyword_and_ignore_error                                    mode=verbose
run_keyword_and_ignore_error (buffered)                                     run_keyword_and_ignore_error                                    mode=buffered
run_keyword_and_return_status                                               run_keyword_and_return_status
run_keyword_and_return_status (verbose)                                     run_keyword_and_return_status                                   mode=verbose
run_keyword_and_return_status (buffered)                                    run_keyword_and_return_status                                   mode=buffered
run_keywords_failing                                                        run_keywords_failing
run_keywords_failing (verbose)                                              run_keywords_failing                                            mode=verbose
run_keywords_failing (buffered)                                             run_keywords_failing                                            mode=buffered
run_keywords_passing                                                        run_keywords_passing
run_keywords_passing (verbose)                                              run_keywords_passing                                            mode=verbose
run_keywords_passing (buffered)                                             run_keywords_passing                                            mode=buffered
run_process                                                                 run_process                                                     --tracesubprocesses
run_process (verbose)                                                       run_process                                                     --tracesubprocesses     mode=verbose
run_process (buffered)                                                      run_process                                                     --tracesubprocesses     mode=buffered
suite_setup_failing                                                         suite_setup_failing
suite_setup_failing (verbose)                                               suite_setup_failing                                             mode=verbose
suite_setup_failing (buffered)                                              suite_setup_failing                                             mode=buffered
suite_setup_failing_testcase                                                suite_setup_failing_testcase
suite_setup_failing_testcase (verbose)                                      suite_setup_failing_testcase                                    mode=verbose
suite_setup_failing_testcase (buffered)                                     suite_setup_failing_testcase                                    mode=buffered
suite_setup_passing                                                         suite_setup_passing
suite_setup_passing (verbose)                                               suite_setup_passing                                             mode=verbose
suite_setup_passing (buffered)                                              suite_setup_passing                                             mode=buffered
suite_setup_run_keyword_and_continue_on_failure_failing                     suite_setup_run_keyword_and_continue_on_failure_failing
suite_setup_run_keyword_and_continue_on_failure_failing (verbose)           suite_setup_run_keyword_and_continue_on_failure_failing         mode=verbose
suite_setup_run_keyword_and_continue_on_failure_failing (buffered)          suite_setup_run_keyword_and_continue_on_failure_failing         mode=buffered
suite_setup_run_keyword_and_continue_on_failure_passing                     suite_setup_run_keyword_and_continue_on_failure_passing
suite_setup_run_keyword_and_continue_on_failure_passing (verbose)           suite_setup_run_keyword_and_continue_on_failure_passing         mode=verbose
suite_setup_run_keyword_and_continue_on_failure_passing (buffered)          suite_setup_run_keyword_and_continue_on_failure_passing         mode=buffered
suite_setup_run_keyword_and_ignore_error_failing                            suite_setup_run_keyword_and_ignore_error_failing
suite_setup_run_keyword_and_ignore_error_failing (verbose)                  suite_setup_run_keyword_and_ignore_error_failing                mode=verbose
suite_setup_run_keyword_and_ignore_error_failing (buffered)                 suite_setup_run_keyword_and_ignore_error_failing                mode=buffered
suite_setup_run_keyword_and_ignore_error_passing                            suite_setup_run_keyword_and_ignore_error_passing
suite_setup_run_keyword_and_ignore_error_passing (verbose)                  suite_setup_run_keyword_and_ignore_error_passing                mode=verbose
suite_setup_run_keyword_and_ignore_error_passing (buffered)                 suite_setup_run_keyword_and_ignore_error_passing                mode=buffered
suite_setup_run_keyword_and_return_status_failing                           suite_setup_run_keyword_and_return_status_failing
suite_setup_run_keyword_and_return_status_failing (verbose)                 suite_setup_run_keyword_and_return_status_failing               mode=verbose
suite_setup_run_keyword_and_return_status_failing (buffered)                suite_setup_run_keyword_and_return_status_failing               mode=buffered
suite_setup_run_keyword_and_return_status_passing                           suite_setup_run_keyword_and_return_status_passing
suite_setup_run_keyword_and_return_status_passing (verbose)                 suite_setup_run_keyword_and_return_status_passing               mode=verbose
suite_setup_run_keyword_and_return_status_passing (buffered)                suite_setup_run_keyword_and_return_status_passing               mode=buffered
suite_setup_warning                                                         suite_setup_warning
suite_setup_warning (verbose)                                               suite_setup_warning                                             mode=verbose
suite_setup_warning (buffered)                                              suite_setup_warning                                             mode=buffered
suite_teardown_failing                                                      suite_teardown_failing
suite_teardown_failing (verbose)                                            suite_teardown_failing                                          mode=verbose
suite_teardown_failing (buffered)                                           suite_teardown_failing                                          mode=buffered
suite_teardown_failing_skipping                                             suite_teardown_failing_skipping                                 expected_rc=0
suite_teardown_failing_skipping (verbose)                                   suite_teardown_failing_skipping                                 mode=verbose            expected_rc=0
suite_teardown_failing_skipping (buffered)                                  suite_teardown_failing_skipping                                 mode=buffered           expected_rc=0
suite_teardown_failing_testcase                                             suite_teardown_failing_testcase
suite_teardown_failing_testcase (verbose)                                   suite_teardown_failing_testcase                                 mode=verbose
suite_teardown_failing_testcase (buffered)                                  suite_teardown_failing_testcase                                 mode=buffered
suite_teardown_failing_twice                                                suite_teardown_failing_twice
suite_teardown_failing_twice (verbose)                                      suite_teardown_failing_twice                                    mode=verbose
suite_teardown_failing_twice (buffered)                                     suite_teardown_failing_twice                                    mode=buffered
suite_teardown_passing                                                      suite_teardown_passing
suite_teardown_passing (verbose)                                            suite_teardown_passing                                          mode=verbose
suite_teardown_passing (buffered)                                           suite_teardown_passing                                          mode=buffered
suite_teardown_run_keyword_and_continue_on_failure_failing                  suite_teardown_run_keyword_and_continue_on_failure_failing
suite_teardown_run_keyword_and_continue_on_failure_failing (verbose)        suite_teardown_run_keyword_and_continue_on_failure_failing      mode=verbose
suite_teardown_run_keyword_and_continue_on_failure_failing (buffered)       suite_teardown_run_keyword_and_continue_on_failure_failing      mode=buffered
suite_teardown_run_keyword_and_continue_on_failure_passing                  suite_teardown_run_keyword_and_continue_on_failure_passing
suite_teardown_run_keyword_and_continue_on_failure_passing (verbose)        suite_teardown_run_keyword_and_continue_on_failure_passing      mode=verbose
suite_teardown_run_keyword_and_continue_on_failure_passing (buffered)       suite_teardown_run_keyword_and_continue_on_failure_passing      mode=buffered
suite_teardown_run_keyword_and_ignore_error_failing                         suite_teardown_run_keyword_and_ignore_error_failing
suite_teardown_run_keyword_and_ignore_error_failing (verbose)               suite_teardown_run_keyword_and_ignore_error_failing             mode=verbose
suite_teardown_run_keyword_and_ignore_error_failing (buffered)              suite_teardown_run_keyword_and_ignore_error_failing             mode=buffered
suite_teardown_run_keyword_and_ignore_error_passing                         suite_teardown_run_keyword_and_ignore_error_passing
suite_teardown_run_keyword_and_ignore_error_passing (verbose)               suite_teardown_run_keyword_and_ignore_error_passing             mode=verbose
suite_teardown_run_keyword_and_ignore_error_passing (buffered)              suite_teardown_run_keyword_and_ignore_error_passing             mode=buffered
suite_teardown_run_keyword_and_return_status_failing                        suite_teardown_run_keyword_and_return_status_failing
suite_teardown_run_keyword_and_return_status_failing (verbose)              suite_teardown_run_keyword_and_return_status_failing            mode=verbose
suite_teardown_run_keyword_and_return_status_failing (buffered)             suite_teardown_run_keyword_and_return_status_failing            mode=buffered
suite_teardown_run_keyword_and_return_status_passing                        suite_teardown_run_keyword_and_return_status_passing
suite_teardown_run_keyword_and_return_status_passing (verbose)              suite_teardown_run_keyword_and_return_status_passing            mode=verbose
suite_teardown_run_keyword_and_return_status_passing (buffered)             suite_teardown_run_keyword_and_return_status_passing            mode=buffered
suite_teardown_warning                                                      suite_teardown_warning
suite_teardown_warning (verbose)                                            suite_teardown_warning                                          mode=verbose
suite_teardown_warning (buffered)                                           suite_teardown_warning                                          mode=buffered
test_setup_failing                                                          test_setup_failing
test_setup_failing (verbose)                                                test_setup_failing                                              mode=verbose
test_setup_failing (buffered)                                               test_setup_failing                                              mode=buffered
test_setup_passing                                                          test_setup_passing
test_setup_passing (verbose)                                                test_setup_passing                                              mode=verbose
test_setup_passing (buffered)                                               test_setup_passing                                              mode=buffered
test_setup_warning                                                          test_setup_warning
test_setup_warning (verbose)                                                test_setup_warning                                              mode=verbose
test_setup_warning (buffered)                                               test_setup_warning                                              mode=buffered
test_teardown_failing                                                       test_teardown_failing
test_teardown_failing (verbose)                                             test_teardown_failing                                           mode=verbose
test_teardown_failing (buffered)                                            test_teardown_failing                                           mode=buffered
test_teardown_passing                                                       test_teardown_passing
test_teardown_passing (verbose)                                             test_teardown_passing                                           mode=verbose
test_teardown_passing (buffered)                                            test_teardown_passing                                           mode=buffered
test_teardown_warning                                                       test_teardown_warning
test_teardown_warning (verbose)                                             test_teardown_warning                                           mode=verbose
test_teardown_warning (buffered)                                            test_teardown_warning                                           mode=buffered
try_catch_exception                                                         try_catch_exception
try_catch_exception (verbose)                                               try_catch_exception                                             mode=verbose
try_catch_exception (buffered)                                              try_catch_exception                                             mode=buffered
try_catch_passing                                                           try_catch_passing
try_catch_passing (verbose)                                                 try_catch_passing                                               mode=verbose
try_catch_passing (buffered)                                                try_catch_passing                                               mode=buffered
var_passing                                                                 var_passing
var_passing (verbose)                                                       var_passing                                                     mode=verbose
var_passing (buffered)                                                      var_passing                                                     mode=buffered
var_failing                                                                 var_failing
var_failing (verbose)                                                       var_failing                                                     mode=verbose
var_failing (buffered)                                                      var_failing                                                     mode=buffered
while_failing                                                               while_failing
while_failing (verbose)                                                     while_failing                                                   mode=verbose
while_failing (buffered)                                                    while_failing                                                   mode=buffered
while_passing                                                               while_passing
while_passing (verbose)                                                     while_passing                                                   mode=verbose
while_passing (buffered)                                                    while_passing                                                   mode=buffered


*** Keywords ***
Run Minimal Testcase
    [Documentation]    Runs one of the minimal testcases and checks that the
    ...    output matches.
    [Arguments]    ${testcase}    @{additional_args}    ${mode}=normal    ${expected_rc}=${None}
    # Compute the testcase file and expected result file.
    VAR    ${testcase_file}    ${TESTCASE_DIR}${/}${testcase}.robot
    VAR    ${testcase_result}    ${TESTCASE_DIR}${/}${testcase}.trace
    IF    ${ROBOT_VERSION_MAJOR} < 7
        IF    os.path.exists("${TESTCASE_DIR}${/}${testcase}.trace.rf6.${mode}")
            VAR    ${testcase_result}    ${testcase_result}.rf6
        END
    END
    IF    "${mode}" == "verbose"
        VAR    ${testcase_result}    ${testcase_result}.verbose.unbuffered
    ELSE IF    "${mode}" == "buffered"
        VAR    ${testcase_result}    ${testcase_result}.verbose.buffered
    ELSE
        VAR    ${testcase_result}    ${testcase_result}.normal
    END
    IF    ${expected_rc} is None
        IF    "failing" in "${testcase}"
            ${match} =    Evaluate    re.search(r"(\\d+)failing", "${testcase}")
            ${expected_rc} =    Set Variable    ${{$match.group(1) if $match else 1}}
        ELSE
            ${expected_rc} =    Set Variable    0
        END
    END
    File Should Exist    ${testcase_file}
    File Should Exist    ${testcase_result}

    # Add any additional arguments.
    IF    "${mode}" in {"verbose", "buffered"}
        Append To List    ${additional_args}    --verbose
    END
    IF    "${mode}" == "buffered"
        VAR    &{env_extra}     ROBOT_TRACE_LIVE_OUTPUT=0
    ELSE
        # robocop: off=VAR01   Intentionally empty dictionary.
        VAR    &{env_extra}
    END

    # Run robot-trace and check the output matches the expectation.
    ${res} =  Run Process Check Output
    ...    robot-trace
    ...    --output      NONE
    ...    --report      NONE
    ...    --log         NONE
    ...    @{additional_args}
    ...    ${testcase_file}
    ...    expected_rc=${expected_rc}
    ...    env_extra=${env_extra}
    Should Be Equal    ${EMPTY}    ${res.stderr}
    ${testcase_expectation} =    Get File    ${testcase_result}
    ${testcase_expectation} =    Strip String    ${testcase_expectation}
    ${normalized_stdout} =    Normalize Output    ${res.stdout}
    ${normalized_expectation} =    Normalize Output    ${testcase_expectation}
    Should Be Equal    ${normalized_expectation}    ${normalized_stdout}
