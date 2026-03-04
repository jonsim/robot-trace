*** Test Cases ***
VAR Failing
    VAR    @{l}    0    1    2
    VAR    ${e}    ${l}[3]
    Log    Line unreachable because ${e} is out-of-range
