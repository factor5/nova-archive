Feature: Book page
  As a reader
  I want a page per book
  So that I can see its awards, my shelf status and related books

  Background:
    Given a fresh browser profile
    And the app is open on the Library tab

  @BP-01 @smoke
  Scenario Outline: Open the book page from different places
    When I <action>
    Then the address ends with "#book/ancillary-justice--ann-leckie"
    And the page heading reads "Ancillary Justice"

    Examples:
      | action                                           |
      | tap the title "Ancillary Justice" on its card    |
      | tap the title in the book preview dialog         |
      | tap the title in a reading list                  |
      | open the address "#book/ancillary-justice--ann-leckie" directly |

  @BP-02
  Scenario: Back returns to where I came from
    Given I opened the book page for "Ancillary Justice" from the Library
    When I tap "← Back"
    Then the Library tab is shown with my previous filters

  @BP-03 @smoke
  Scenario: Awards table lists every nomination
    When I open the book page for "Ancillary Justice"
    Then the awards table has 6 rows
    And the rows are ordered newest year first
    And a winning row shows "★ Winner" on one line
    And the Hugo 2014 row is a winner

  @BP-04
  Scenario: More by the same author
    When I open the book page for "Ancillary Justice"
    Then "More by Ann Leckie" lists "Ancillary Sword", "Ancillary Mercy", "Provenance" and "Translation State"
    And "Ancillary Sword" shows 2 stars when I rated it 2

  @BP-05
  Scenario: Same awards, same year
    When I open the book page for "Ancillary Justice"
    Then 6 groups are shown, for Hugo 2014, Clarke 2014, Campbell 2014, PKD 2014, Nebula 2013 and BSFA 2013
    And the Hugo 2014 group lists "Neptune's Brood", "Parasite", "The Wheel of Time" and "Warbound"
    And "Ancillary Justice" itself is not listed in its own groups

  @BP-06
  Scenario: Each group is capped at 12 books
    When I open a book page whose award-year has more than 12 other books
    Then that group shows 12 books

  @BP-07 @smoke
  Scenario: My shelf controls work on the page
    Given I open the book page for "Dune"
    When I tap "Mark read"
    Then the page shows "✓ Read", five stars and a "Finished on" date
    When I tap star 4
    Then 4 stars are filled
    When I tap "▶ Start" on a different unread book's page
    Then the "Now reading" row shows that book

  @BP-08
  Scenario: List chips
    Given "Dune" is on the lists "A" and "B"
    When I open the book page for "Dune"
    Then chips "A" and "B" are shown
    When I tap the chip "A"
    Then the "My Lists" tab opens on the list "A"

  @BP-09
  Scenario: Author button filters the library
    When I open the book page for "Ancillary Justice"
    And I tap the author "Ann Leckie"
    Then the Library shows 5 books for the search "leckie"

  @BP-10
  Scenario: Unknown book id
    When I open the address "#book/does-not-exist"
    Then the message "Book not found" is shown
    And a way back to the Library is offered

  @BP-11
  Scenario: Reload keeps me on the page
    Given I am on the book page for "Dune"
    When I reload
    Then the book page for "Dune" is shown

  @BP-12
  Scenario: Browser back and forward follow the page changes
    Given I opened the book page for "Dune" and then the "About" tab
    When I press the browser Back button
    Then the book page for "Dune" is shown

  @BP-13 @mobile
  Scenario: The page fits a phone
    Given a 390 px wide screen
    When I open the book page for "Ancillary Justice"
    Then nothing overflows horizontally
    And every panel has inner padding

  @BP-14
  Scenario: Opening a page starts at the top
    Given I scrolled far down the Library
    When I open a book page
    Then the page is scrolled to the top
