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


*** Test Cases ***
# robocop: off=NAME07  It's useful to have the test case names match the file.
basic_failing                       basic_failing
basic_passing                       basic_passing
basic_skipping                      basic_skipping
for_failing                         for_failing
for_passing                         for_passing
if_else_failing                     if_else_failing
if_else_passing                     if_else_passing
invalid_syntax                      invalid_syntax                      expected_rc=1
log_debug                           log_debug                           --loglevel=DEBUG
log_error                           log_error
log_multiline                       log_multiline
log_warning                         log_warning
multiple_2failing                   multiple_2failing
multiple_passing                    multiple_passing
nested_keywords_1                   nested_keywords_1
nested_keywords_2                   nested_keywords_2
nested_keywords_3                   nested_keywords_3
nested_keywords_failing             nested_keywords_failing
run_keywords_failing                run_keywords_failing
run_keywords_passing                run_keywords_passing
suite_setup_failing                 suite_setup_failing
suite_setup_failing_testcase        suite_setup_failing_testcase
suite_setup_passing                 suite_setup_passing
suite_setup_warning                 suite_setup_warning
suite_teardown_failing              suite_teardown_failing
suite_teardown_failing_testcase     suite_teardown_failing_testcase
suite_teardown_passing              suite_teardown_passing
suite_teardown_warning              suite_teardown_warning
test_setup_failing                  test_setup_failing
test_setup_passing                  test_setup_passing
test_setup_warning                  test_setup_warning
test_teardown_failing               test_teardown_failing
test_teardown_passing               test_teardown_passing
test_teardown_warning               test_teardown_warning
try_catch_exception                 try_catch_exception
try_catch_passing                   try_catch_passing


*** Keywords ***
Run Minimal Testcase
    [Documentation]    Runs one of the minimal testcases and checks that the
    ...    output matches.
    [Arguments]    ${testcase}    @{additional_args}    ${expected_rc}=0
    ${testcase_file} =    Set Variable    ${TESTCASE_DIR}${/}${testcase}.robot
    ${testcase_result} =    Set Variable    ${TESTCASE_DIR}${/}${testcase}.trace.normal
    IF    ${ROBOT_VERSION_MAJOR} < 7
        IF    os.path.exists("${TESTCASE_DIR}${/}${testcase}.trace.rf6.normal")
            ${testcase_result} =    Set Variable    ${TESTCASE_DIR}${/}${testcase}.trace.rf6.normal
        END
    END
    IF    "failing" in "${testcase}" and ${expected_rc} == 0
        ${match} =    Evaluate    re.search(r"(\\d+)failing", "${testcase}")
        ${expected_rc} =    Set Variable    ${{$match.group(1) if $match else 1}}
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
