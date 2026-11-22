Feature: Data and repository integrity
  As the maintainer
  I want the dataset and repo files checked mechanically
  So that a bad edit cannot be merged
  (These run without a browser; see tests/support/check_repo.py)

  @DI-01 @smoke
  Scenario: data.json is well formed
    Given data.json
    Then it is a JSON array of 1329 books
    And every book has string "id", "title", "author" and a list "entries"

  @DI-02
  Scenario: Ids are unique and stable
    Then no two books share an id
    And every id equals the slug of title and author joined by "--"

  @DI-03
  Scenario: Entries are valid
    Then every entry has an "award" from the 7 known awards
    And "year" is an integer between 1950 and the current year
    And "result" is "winner" or "finalist"

  @DI-04
  Scenario: No duplicate entries
    Then a book has at most one entry per award and year and result

  @DI-05
  Scenario: Every book has at least one entry
    Then no book has an empty entries list

  @DI-06
  Scenario: Facts file matches the data
    When I run "python3 tests/support/gen_facts.py --check"
    Then it exits 0, meaning tests/fixtures/facts.json is current
    And the facts agree with the scenarios: 296 books with a win and 629 authors

  @DI-07
  Scenario: The dataset is reproducible from its source
    When I run "python3 tools/parse.py" into a temporary file
    Then the output is byte-identical to data.json

  @DI-08
  Scenario: Text is clean
    Then no title or author has leading or trailing spaces, double spaces or control characters

  @DI-10 @smoke
  Scenario: Version numbers agree
    Then the VERSION in sw.js, every "?v=" in index.html and the app-version meta are the same number

  @DI-11
  Scenario: Precache list is complete
    Then the SHELL list in sw.js names every css/*.css and js/*.js file and each listed file exists

  @DI-12
  Scenario: Every file referenced from index.html and the manifest exists
    Then stylesheets, scripts, icons and the manifest link all resolve

  @DI-13
  Scenario: JavaScript modules parse and their imports resolve
    Then "node --check" passes for every js/*.js file
    And every relative import points to an existing file

  @DI-14 @smoke
  Scenario: No secrets are committed
    Then no file contains a private key block, a service-account JSON or an API secret
    And firebase-config.js holds only the public web config

  @DI-15
  Scenario: Licence and docs exist
    Then LICENSE, README.md, IDEAS.md, tools/README.md and tests/README.md exist

  @DI-16
  Scenario: Every feature scenario has a unique id tag
    Then every Scenario in tests/features has exactly one id tag like @LIB-03
    And no id is used twice
