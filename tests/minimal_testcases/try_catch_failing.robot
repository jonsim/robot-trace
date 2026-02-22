*** Test Cases ***
TRY-CATCH Failing Branch
    TRY
        Log    Entered TRY
        ${result}=    Evaluate    1 + 1
        Should Be Equal As Numbers    ${result}    4
    EXCEPT
        Log    Entered EXCEPT
    END
