*** Settings ***
Library    Process


*** Test Cases ***
Run A Subprocess
    Run Process    python  -c  print('Hello World')
