*** Test Cases ***
FOR Failing
    FOR    ${i}    IN RANGE    5
        Log    Iteration ${i}
        ${result}=    Evaluate    ${i} + ${i}
        Should Be Equal As Numbers    ${result}    ${i}
    END
