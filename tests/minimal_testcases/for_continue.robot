*** Test Cases ***
FOR CONTINUE
    FOR    ${i}    IN RANGE    5
        Log    Iteration ${i}
        IF    ${i} < 3    CONTINUE
        ${result}=    Evaluate    ${i} + ${i}
        Should Be Equal As Numbers    ${result}    ${{$i * 2}}
    END
