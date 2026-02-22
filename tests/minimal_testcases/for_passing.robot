*** Test Cases ***
FOR Passing
    FOR    ${i}    IN RANGE    5
        Log    Iteration ${i}
        ${result}=    Evaluate    (${i} + ${i}) / 2
        Should Be Equal As Numbers    ${result}    ${i}
    END
