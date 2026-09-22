*** Settings ***
Library    Process


*** Test Cases ***
Run A Subprocess And Redirect Output
    Run Process    python  -c  print('Hello World')
    ...    stdout=${TEMPDIR}/run_process_redirect_stdout.txt
    ...    stderr=STDOUT
