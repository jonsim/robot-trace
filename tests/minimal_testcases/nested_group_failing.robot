*** Test Cases ***
Nested GROUP Failing
    Log    Outside groups
    GROUP    Initial group
        Log    Inside initial group
    END
    GROUP    First level group
        Log    Inside group 1
        GROUP    Second level group
            Log    Inside group 2
            Fail    Bad things happened
        END
    END
    GROUP    Unreachable group
        Log    Inside unreachable group
    END
