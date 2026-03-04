*** Test Cases ***
Nested GROUP Passing
    Log    Outside groups
    GROUP    First level group
        Log    Inside group 1
        GROUP    Second level group
            Log    Inside group 2
        END
    END
