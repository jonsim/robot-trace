*** Test Cases ***
GROUP Failing
    Log    Hello World
    GROUP
        Log    Inside anonymous group
        Fail   Bad things happened
    END
