Feature: My own books
  As a reader
  I want to add books that are not on any award list
  So that my reading history is complete

  Background:
    Given a fresh browser profile
    And the app is open on the Library tab

  # ---------- adding ----------

  @MB-01 @smoke
  Scenario: Add a book by hand
    When I tap "＋ Add a book"
    Then a dialog "Add a book" opens with Title, Author and Year fields
    When I enter title "Convenience Store Woman", author "Sayaka Murata", year "2016" and tap "Add"
    Then the toast "Added “Convenience Store Woman”" is shown
    And searching for "convenience" finds "Convenience Store Woman"
    And the saved data has a custom book with id "my--convenience-store-woman--murata"

  @MB-02
  Scenario Outline: Validation
    When I open the add dialog and enter title "<title>", author "<author>", year "<year>"
    And I tap "Add"
    Then the message "<message>" is shown
    And nothing is added

    Examples:
      | title    | author | year | message                                   |
      |          | X      |      | Please enter a title and an author.       |
      | Convenience Store Woman |        |      | Please enter a title and an author.       |
      | Convenience Store Woman | Clarke | 84   | Year should be four digits, for example 1984. |
      | Convenience Store Woman | Clarke | abcd | Year should be four digits, for example 1984. |

  @MB-03
  Scenario: Year is optional
    When I add title "Convenience Store Woman" by "Sayaka Murata" without a year
    Then the book exists and appears under "No year" when grouped by decade

  @MB-04 @smoke
  Scenario: Duplicates of award books are refused
    When I try to add "The Left Hand of Darkness" by "Ursula K. Le Guin"
    Then the message "Already in your library: The Left Hand of Darkness" is shown
    And nothing is added

  @MB-05
  Scenario: Duplicates of my own books are refused, ignoring case and punctuation
    Given I added "Convenience Store Woman" by "Sayaka Murata"
    When I try to add "CONVENIENCE STORE WOMAN!" by "sayaka murata"
    Then the "Already in your library" message is shown

  @MB-06
  Scenario: Id collisions get a numeric suffix
    Given I added "Convenience Store Woman" by "Sayaka Murata"
    When I add "Convenience Store Woman" by "Someone Murata"
    Then the second id is "my--convenience-store-woman--murata-2"

  @MB-07
  Scenario: Text is shown literally
    When I add title "<b>X</b>" by "A <i>B</i>"
    Then the card shows the text "<b>X</b>" with no markup applied

  # ---------- Open Library search ----------

  @MB-10 @ol-mock
  Scenario: Search Open Library and fill the form
    Given Open Library returns results for "ancillary"
    When I type "ancillary" in the dialog's search box and tap "Search"
    Then up to 5 results with title, author and year are listed
    When I tap the first result
    Then Title, Author and Year are filled in

  @MB-11 @ol-mock
  Scenario: No results
    Given Open Library returns nothing for "zzzz"
    When I search for "zzzz"
    Then the message "No matches. You can still type the details below." is shown

  @MB-12 @ol-mock
  Scenario: Open Library is unreachable
    Given Open Library requests fail
    When I search for "dune"
    Then the message "Search unavailable. You can still type the details below." is shown
    And the manual form still works

  @MB-13
  Scenario: Search is hidden when Open Library lookups are switched off
    Given I switched off Open Library lookups on the About page
    When I open the add dialog
    Then there is no search box and the manual form is shown

  # ---------- library behaviour ----------

  @MB-20 @smoke
  Scenario: My books are findable and marked
    Given I added "Convenience Store Woman" by "Sayaka Murata" (2016)
    When I search for "convenience"
    Then the card shows a "My book" tag and no award entries

  @MB-21
  Scenario: Source filter
    Given I added "Convenience Store Woman"
    When I choose "My books" in the "Source" filter
    Then only "Convenience Store Woman" is listed
    When I choose "Award books"
    Then "Convenience Store Woman" is not listed

  @MB-22
  Scenario Outline: Award filters hide my books
    Given I added "Convenience Store Woman"
    When I apply the filter "<filter>"
    Then "Convenience Store Woman" is not listed

    Examples:
      | filter           |
      | Award: Hugo      |
      | Winners only     |

  @MB-23
  Scenario: Decade filter uses the year I gave
    Given I added "Convenience Store Woman" (2016) and "Old Book" (1955)
    When I filter by the 2010s
    Then "Convenience Store Woman" is listed and "Old Book" is not

  @MB-24
  Scenario: Grouping
    Given I added "Convenience Store Woman" (2016) and "Undated" without a year
    When I group by "Award"
    Then both appear under "My books"
    When I group by "Decade"
    Then "Convenience Store Woman" is under "2010s" and "Undated" under "No year"

  @MB-25
  Scenario: Read status, rating, notes and lists work as for any book
    Given I added "Convenience Store Woman"
    When I mark it read, rate it 5 stars, add the note "Loved it" and add it to a list
    Then all four are saved under its id

  # ---------- editing and deleting ----------

  @MB-30 @smoke
  Scenario: Edit my book
    Given I added "Convenience Store Woman" by "Sayaka Murata"
    When I open its book page
    Then a "Your book details" panel with Title, Author and Year is shown
    When I change the year to "2021" and tap "Save"
    Then the page shows 2021

  @MB-31
  Scenario: Editing into a duplicate is refused
    Given I added "Convenience Store Woman" and "Other"
    When I rename "Other" to "Convenience Store Woman" with the same author
    Then the message "Another book with this title and author already exists." is shown

  @MB-32 @smoke
  Scenario: Delete my book
    Given I added "Convenience Store Woman", marked it read, rated it, noted it and listed it
    When I tap "Delete book" twice to confirm
    Then the toast "Book deleted" is shown
    And the Library is shown without "Convenience Store Woman"
    And its read mark, rating, note and list entries are gone from the saved data

  @MB-33
  Scenario: Award books have no edit panel
    When I open the book page for "Dune"
    Then there is no "Your book details" panel

  # ---------- persistence ----------

  @MB-40
  Scenario: My books survive a reload and sync
    Given I added "Convenience Store Woman" while signed in
    When I reload the page
    Then "Convenience Store Woman" is still there
    And the cloud document has it in the "custom" field

  @MB-41
  Scenario: About counts are unaffected
    Given I added "Convenience Store Woman"
    When I open the "About" tab
    Then the award totals are the same as before
