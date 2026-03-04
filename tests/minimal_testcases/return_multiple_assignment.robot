*** Test Cases ***
RETURN Multiple Assignment
    ${a}    ${b}    ${c}=    Return Multiple Values
    Log    ${a}, ${b}, ${c}


*** Keywords ***
Return Multiple Values
    RETURN    cat    dog    fish
