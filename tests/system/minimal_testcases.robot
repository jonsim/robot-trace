*** Settings ***
Documentation     Runs each of the minimal testcases in ../minimal_testcases and
...    checks the output matches.
Library           OperatingSystem
Library           String
Resource          common.resource
Test Template     Run Minimal Testcase


*** Variables ***
${TESTCASE_DIR}    ${CURDIR}${/}..${/}minimal_testcases


*** Test Cases ***
# robocop: off=NAME07  It's useful to have the test case names match the file.
basic_failing               basic_failing               expected_rc=1
basic_passing               basic_passing
basic_skipping              basic_skipping
for_failing                 for_failing                 expected_rc=1
for_passing                 for_passing
if_else_failing             if_else_failing             expected_rc=1
if_else_passing             if_else_passing
invalid_syntax              invalid_syntax              expected_rc=1
log_debug                   log_debug                   --log-level=DEBUG
log_error                   log_error
log_multiline               log_multiline
log_warning                 log_warning
multiple_failing            multiple_failing            expected_rc=2
multiple_passing            multiple_passing
nested_keywords_1           nested_keywords_1
nested_keywords_2           nested_keywords_2
nested_keywords_3           nested_keywords_3
nested_keywords_failing     nested_keywords_failing     expected_rc=1
suite_setup_failing         suite_setup_failing         expected_rc=1
suite_setup_passing         suite_setup_passing
suite_setup_warning         suite_setup_warning
suite_teardown_failing      suite_teardown_failing      expected_rc=1
suite_teardown_passing      suite_teardown_passing
suite_teardown_warning      suite_teardown_warning
test_setup_failing          test_setup_failing          expected_rc=1
test_setup_passing          test_setup_passing
test_setup_warning          test_setup_warning
test_teardown_failing       test_teardown_failing       expected_rc=1
test_teardown_passing       test_teardown_passing
test_teardown_warning       test_teardown_warning
try_catch_failing           try_catch_failing
try_catch_passing           try_catch_passing


*** Keywords ***
Run Minimal Testcase
    [Documentation]    Runs one of the minimal testcases and checks that the
    ...    output matches.
    [Arguments]    ${testcase}    @{additional_args}    ${expected_rc}=0
    VAR    ${testcase_file}         ${TESTCASE_DIR}${/}${testcase}.robot
    VAR    ${testcase_result}       ${TESTCASE_DIR}${/}${testcase}.trace.normal
    ${res} =  Run Process Check Output
    ...    robot-cli
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
