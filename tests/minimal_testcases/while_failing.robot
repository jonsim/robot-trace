*** Test Cases ***
WHILE Failing
    VAR    ${i}    0
    WHILE    ${i} < 5
        Log    ${i} is still less than 5
        ${i} =    Evaluate    ${i}++
    END
