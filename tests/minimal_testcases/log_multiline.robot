*** Test Cases ***
Log Multiline
    Log    In the multiline testcase\nHere's a box:
    Draw A Box


*** Keywords ***
Draw A Box
    Log    +-------+\n| hello |\n+-------+
