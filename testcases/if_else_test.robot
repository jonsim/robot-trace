*** Settings ***
Library     Collections


*** Test Cases ***
IF-ELSE Shows Only Taken Branch
    IF    True
        Log    Taken branch - should appear
        ${result}=    Evaluate    1 + 1
        Should Be Equal As Numbers    ${result}    2
    ELSE
        Log    NOT taken branch - should NOT appear
        Fail    This should not run
    END

IF-ELSE Fail On Taken Branch
    IF    True
        Log    About to fail
        Should Be Equal As Numbers    1    2    msg=Intentional failure
    ELSE
        Log    NOT taken branch
    END
