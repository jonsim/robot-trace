*** Test Cases ***
FOR BREAK
    FOR    ${i}    IN RANGE    5
        Log    Iteration ${i}
        IF    ${i} == 3    BREAK
        ${result}=    Evaluate    ${i} + ${i}
        Should Be Equal As Numbers    ${result}    ${{$i * 2}}
    END
