*** Test Cases ***
IF-ELSE Passing Branch
    IF    True
        Log    Taken branch - should appear
        ${result}=    Evaluate    1 + 1
        Should Be Equal As Numbers    ${result}    2
    ELSE
        Log    NOT taken branch - should NOT appear
        ${result}=    Evaluate    1 + 1
        Should Be Equal As Numbers    ${result}    4
    END
