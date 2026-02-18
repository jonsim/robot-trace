*** Test Cases ***
Nested Passing Test Case
    Level One Keyword

Nested Failing Test Case
    Level Two Keyword    ${True}

*** Keywords ***
Level One Keyword
    Log    In the level one keyword
    Level Two Keyword    ${False}

Level Two Keyword
    [Arguments]    ${should_fail}
    Log    In the level two keyword
    Level Three Keyword
    IF    ${should_fail}
        Failing Keyword
    END

Level Three Keyword
    Log    In the level three keyword

Failing Keyword
    Log    In the failing keyword
    Fail    This keyword failed