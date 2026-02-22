*** Test Cases ***
IF-ELSE Failing Branch
    IF    1 > 2
        Log    NOT taken branch - should not appear
        ${result}=    Evaluate    1 + 1
        Should Be Equal As Numbers    ${result}    2
    ELSE
        Log    Taken branch - should appear
        ${result}=    Evaluate    1 + 1
        Should Be Equal As Numbers    ${result}    4
    END
