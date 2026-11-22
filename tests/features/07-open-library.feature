Feature: Open Library enrichment
  As a reader
  I want covers, descriptions and subjects on the book page
  So that I get more context without leaving the app
  (All scenarios use the mocked Open Library; see tests/README.md)

  Background:
    Given a fresh browser profile
    And Open Library is mocked

  @OL-01 @smoke @ol-mock
  Scenario: Book page is enriched
    Given Open Library knows "Ancillary Justice" by "Ann Leckie"
    When I open the book page for "Ancillary Justice"
    Then a cover image, a description and subject chips appear
    And a "Open Library" attribution link is shown

  @OL-02 @ol-mock
  Scenario: The page works before enrichment arrives
    Given Open Library responds after 3 seconds
    When I open the book page for "Ancillary Justice"
    Then the awards table is shown immediately
    And the enrichment panel is added when the response arrives

  @OL-03 @ol-mock
  Scenario: No match shows nothing extra
    Given Open Library returns no results
    When I open the book page for "Ancillary Justice"
    Then no enrichment panel is shown and no error is displayed

  @OL-04 @ol-mock
  Scenario: Network failure is silent
    Given Open Library requests fail
    When I open the book page for "Ancillary Justice"
    Then the page renders normally with no error message

  @OL-05 @ol-mock
  Scenario: Requests time out after 8 seconds
    Given Open Library never responds
    When I open the book page and wait 9 seconds
    Then no enrichment panel is shown
    And the page is still usable

  @OL-06 @ol-mock
  Scenario: Results are cached
    Given Open Library knows "Ancillary Justice"
    When I open its book page, go back and open it again
    Then Open Library was asked only once
    And the cache entry is kept under "nova-ol-v1"

  @OL-07 @ol-mock
  Scenario: Misses are cached for a shorter time
    Given Open Library returns no results
    When I open the book page twice
    Then Open Library was asked only once
    And the cache entry expires after 1 day, hits after 30 days

  @OL-08 @ol-mock
  Scenario: Descriptions are cleaned
    Given the description contains markdown links, a "[1]: http://x" footnote line and "----------" rules
    When I open the book page
    Then the description shows plain text with no footnote or rule lines

  @OL-09 @ol-mock
  Scenario: Remote text cannot inject markup
    Given the description is "<img src=x onerror=alert(1)>"
    When I open the book page
    Then the text is shown literally and no script runs

  @OL-10 @smoke @ol-mock
  Scenario: Switching lookups off
    When I open the "About" tab and switch off Open Library lookups
    And I open the book page for "Ancillary Justice"
    Then no request to openlibrary.org is made
    And no enrichment panel is shown
    And the flag "nova-ol-off" is saved

  @OL-11
  Scenario: The switch can be turned back on
    Given lookups are switched off
    When I switch them on and open a book page
    Then Open Library is asked again

  @OL-12 @ol-mock
  Scenario: Custom books are enriched too
    Given I added "Convenience Store Woman" by "Sayaka Murata"
    When I open its book page
    Then Open Library is asked for the title "Convenience Store Woman" and the author "Sayaka Murata"

  @OL-13 @ol-mock
  Scenario: Only the title and author are sent
    When I open any book page
    Then the request contains no user id, notes, ratings or list names
