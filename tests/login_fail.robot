*** Settings ***
Library  SeleniumLibrary
Library  Process

Suite Setup         Start the webserver

Suite Teardown      Stop the webserver

*** Keywords ***
Start the webserver
    Log To Console  start
    ${process}=     Start Process       python3     -m      coverage    run     --source    src    -m      streamlit    run    HOME.py     --server.port       8505    --server.headless   true

    Set suite variable    ${process}
    Log To Console     ${process}
    sleep  2s

Stop the webserver
    Log To Console  end
    Terminate Process    ${process}


*** Variables ***
${URL}             http://localhost:8505/bngblaster
${BROWSER}         headlessfirefox

*** Test Cases ***
login fail test
    Log To Console  test1
    Open Browser  ${URL}  browser=${BROWSER}
    sleep   5
    Page Should Contain     Use button below for login by Google
    Close Browser
