*** Test Cases ***
FOR Multiple Assignment
    FOR    ${animal}    ${place}    IN
    ...    CAT          HALL
    ...    DOG          GARDEN
    ...    FISH         BOWL
        Log    ${animal} ${place}
    END
