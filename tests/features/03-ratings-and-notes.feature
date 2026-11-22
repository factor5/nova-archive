Feature: Ratings, finish dates and notes
  As a reader
  I want to rate the books I have read and keep private notes
  So that I remember what I thought

  Background:
    Given a fresh browser profile
    And the app is open on the Library tab

  @RN-01 @smoke
  Scenario: Only read books can be rated
    Then the card for "Dune" shows no stars
    When I tap "Mark read" on "Dune"
    Then the card for "Dune" shows five empty stars and an "✎ Add note" button

  @RN-02 @smoke
  Scenario Outline: Rate a book by tapping a star
    Given I tapped "Mark read" on "Dune"
    When I tap star <n> on "Dune"
    Then <n> stars are filled on "Dune"
    And the saved data has rating <n> for "dune--frank-herbert"

    Examples:
      | n |
      | 1 |
      | 3 |
      | 5 |

  @RN-03
  Scenario: Tapping the same star again clears the rating
    Given I rated "Dune" 4 stars
    When I tap star 4 on "Dune"
    Then no stars are filled on "Dune"
    And the saved data has no rating for "dune--frank-herbert"

  @RN-04
  Scenario: Changing the rating
    Given I rated "Dune" 4 stars
    When I tap star 2 on "Dune"
    Then 2 stars are filled on "Dune"

  @RN-05
  Scenario: Stars are accessible buttons
    Given I tapped "Mark read" on "Dune"
    Then each star is a button labelled "1 star", "2 stars", "3 stars", "4 stars" and "5 stars"
    And a filled star has aria-pressed "true" and an empty one "false"

  @RN-10 @smoke
  Scenario: Add a note to a read book
    Given I tapped "Mark read" on "Dune"
    When I tap "✎ Add note" on "Dune"
    Then a dialog titled "Dune" opens with five stars and a notes box
    When I type "Spice must flow" and tap "Save"
    Then the dialog closes
    And the toast "Saved" is shown
    And the button on the card now reads "✎ Notes"
    And the saved data has the note "Spice must flow" for "dune--frank-herbert"

  @RN-11
  Scenario: Notes can be edited and cleared
    Given I saved the note "Spice must flow" for "Dune"
    When I open the note dialog for "Dune"
    Then the notes box contains "Spice must flow"
    When I clear the box and tap "Save"
    Then the button on the card reads "✎ Add note" again
    And the saved data has no note for "dune--frank-herbert"

  @RN-12
  Scenario: Notes are trimmed and limited to 2000 characters
    Given I tapped "Mark read" on "Dune"
    When I open the note dialog for "Dune"
    And I type 2100 characters
    Then the notes box holds 2000 characters
    When I replace it with "   spaced   " and tap "Save"
    Then the saved note is "spaced"

  @RN-13
  Scenario: Closing the dialog by clicking outside does not save the notes
    Given I tapped "Mark read" on "Dune"
    And I opened the note dialog for "Dune" and typed "draft"
    When I click outside the dialog
    Then the dialog closes
    And the saved data has no note for "dune--frank-herbert"

  @RN-14
  Scenario: Stars in the dialog save immediately
    Given I tapped "Mark read" on "Dune"
    And I opened the note dialog for "Dune"
    When I tap star 5 in the dialog
    Then 5 stars are filled in the dialog and on the card behind it

  @RN-15
  Scenario: A book being read can have notes but no stars
    Given I started reading "Hyperion"
    Then the card for "Hyperion" shows "✎ Add note" and no stars

  @RN-16
  Scenario: Notes are shown as text, never as markup
    Given I tapped "Mark read" on "Dune"
    When I save the note "<b>bold</b> & <script>alert(1)</script>" for "Dune"
    And I open the note dialog for "Dune"
    Then the notes box contains exactly "<b>bold</b> & <script>alert(1)</script>"
    And no script ran and no bold text appeared

  @RN-17
  Scenario: Un-marking a book keeps its rating and notes for later
    Given I rated "Dune" 4 stars and saved the note "Great" for it
    When I tap "✓ Read" on "Dune"
    Then the card shows no stars
    When I tap "Mark read" on "Dune"
    Then 4 stars are filled and the button reads "✎ Notes"

  @RN-20
  Scenario: Filter and sort by my rating
    Given I rated "Dune" 5 stars and "Hyperion" 3 stars and "Neuromancer" 4 stars
    When I choose "Rated by me" in the "Status" filter
    Then the result count reads "3 books match"
    When I choose "My rating" in the "Sort" filter
    Then the cards are "Dune", "Neuromancer", "Hyperion"

  @RN-30
  Scenario: Finish date is today when I finish a book
    Given I started reading "Hyperion"
    When I tap "✓ Finish" on "Hyperion" and then "Save"
    And I open the book page for "Hyperion"
    Then the "Finished on" date shows today

  @RN-31
  Scenario: Finish date can be corrected on the book page
    Given I tapped "Mark read" on "Dune"
    And I open the book page for "Dune"
    When I set "Finished on" to the 1st of last month
    Then the saved data has that date for "dune--frank-herbert"
    And the date cannot be set in the future

  @RN-32
  Scenario: Finish date can be cleared
    Given I finished "Hyperion" today
    When I clear the "Finished on" date on its book page
    Then the saved data has no finish date for "hyperion--dan-simmons"
