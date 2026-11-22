Feature: Reading status
  As a reader
  I want to mark books as read, start reading them and finish them
  So that I always know where I am

  Background:
    Given a fresh browser profile
    And the app is open on the Library tab

  # ---------- mark read ----------

  @RS-01 @smoke
  Scenario: Mark a book as read and undo it
    When I tap "Mark read" on "Dune"
    Then "Dune" shows a "✓ Read" button and a check mark next to its title
    And the header counter reads "Read 1 / 1329"
    And the saved data lists "dune--frank-herbert" as read
    When I tap "✓ Read" on "Dune"
    Then "Dune" shows a "Mark read" button again
    And the header counter reads "Read 0 / 1329"

  @RS-02
  Scenario: The progress bar follows the read count
    When I mark 133 books as read
    Then the header counter reads "Read 133 / 1329"
    And the progress bar is about 10 percent full

  @RS-03 @smoke
  Scenario: Read marks survive a reload
    Given I tapped "Mark read" on "Dune"
    When I reload the page
    Then "Dune" shows a "✓ Read" button
    And the header counter reads "Read 1 / 1329"

  @RS-04
  Scenario Outline: Filter by status
    Given I tapped "Mark read" on "Dune"
    And I tapped "▶ Start" on "Hyperion"
    When I choose "<status>" in the "Status" filter
    Then the result count reads "<count>"

    Examples:
      | status       | count             |
      | All books    | 1329 books match  |
      | Not read yet | 1328 books match  |
      | Reading now  | 1 book match    |
      | Already read | 1 book match    |

  # ---------- start / stop ----------

  @RS-10 @smoke
  Scenario: Start reading a book
    When I tap "▶ Start" on "Hyperion"
    Then the toast "Started reading" is shown
    And "Hyperion" shows "✓ Finish" and "Stop" buttons and no "Mark read" button
    And a "Now reading" row appears above the tabs with one card "Hyperion"
    And that card shows the author "Dan Simmons" and "Day 1"
    And the saved data has "hyperion--dan-simmons" under reading

  @RS-11
  Scenario: Stop reading a book without finishing it
    Given I started reading "Hyperion"
    When I tap "Stop" on "Hyperion"
    Then "Hyperion" shows "Mark read" and "▶ Start" buttons again
    And the "Now reading" row is gone
    And "Hyperion" is not marked read

  @RS-12
  Scenario: A book that is read cannot be started
    Given I tapped "Mark read" on "Dune"
    Then "Dune" shows no "▶ Start" button

  @RS-13
  Scenario: Marking a book that is being read as read is done by finishing it
    Given I started reading "Hyperion"
    Then "Hyperion" shows no "Mark read" button
    When I tap "✓ Finish" on "Hyperion"
    Then "Hyperion" shows a "✓ Read" button
    And the "Now reading" row is gone

  @RS-14
  Scenario: Reading status survives a reload
    Given I started reading "Hyperion"
    When I reload the page
    Then the "Now reading" row shows "Hyperion"

  # ---------- finishing ----------

  @RS-20 @smoke
  Scenario: Finishing a book opens the rating and notes dialog
    Given I started reading "Hyperion"
    When I tap "✓ Finish" on "Hyperion"
    Then "Hyperion" is marked read
    And a dialog titled "Hyperion" opens with five stars, a notes box and a "Save" button
    And the saved data has a finish date of today for "hyperion--dan-simmons"
    When I tap "Save"
    Then the dialog closes

  @RS-21
  Scenario: Finishing from the Now reading preview
    Given I started reading "Hyperion"
    When I tap the "Hyperion" card in the "Now reading" row
    And I tap "✓ Finish" in the preview
    Then the preview closes and the rating dialog opens

  # ---------- Now reading row ----------

  @RS-30 @smoke
  Scenario: Several books can be read at once and keep their order
    When I tap "▶ Start" on "Dune"
    And I tap "▶ Start" on "Hyperion"
    Then the "Now reading" row header reads "Now reading 2 · swipe →"
    And the cards in the row are "Dune" then "Hyperion"
    When I tap "▶ Start" on "Neuromancer"
    Then the cards in the row are "Dune", "Hyperion", "Neuromancer"

  @RS-31
  Scenario: Stopping one book keeps the others in place
    Given I started reading "Dune", "Hyperion" and "Neuromancer" in that order
    When I tap "Stop" on "Hyperion"
    Then the cards in the row are "Dune" and "Neuromancer"

  @RS-32
  Scenario: A Now reading card is compact
    Given I started reading "Hyperion"
    Then the card in the row shows only the title, the author, "Day 1" and a "›"
    And it has no buttons
    And the card is no taller than 90 pixels on a phone

  @RS-33
  Scenario: The day counter counts days since the start
    Given I started reading "Hyperion" 3 days ago
    Then its card in the row shows "Day 4"

  @RS-34
  Scenario: A note on a book being read is hinted on its card
    Given I started reading "Hyperion"
    And I saved the note "Slow start" for it
    Then the card shows a "✎" before the "›"

  @RS-35 @smoke
  Scenario: Tapping a Now reading card opens a preview with every action
    Given I started reading "Hyperion"
    When I tap the "Hyperion" card in the "Now reading" row
    Then a dialog shows the full card for "Hyperion"
    And the preview has "Open full page ›", "✓ Finish", "Stop", "＋ List", "✎ Add note" and "Close"
    When I tap "Stop" in the preview
    Then the preview now shows "Mark read" and "▶ Start"
    And the "Now reading" row is gone

  @RS-36
  Scenario: The preview updates in place when I act on it
    Given I started reading "Hyperion"
    And I opened its preview
    When I tap "✎ Add note", write "Great", and save
    Then I am back in the app and the "Now reading" card shows a "✎"

  @RS-37
  Scenario: Open the book page from the preview
    Given I opened the preview of a book being read
    When I tap "Open full page ›"
    Then the preview closes
    And the book page for that book is shown

  @RS-38
  Scenario: Cards can be opened with the keyboard
    Given I started reading "Hyperion"
    When I focus the "Hyperion" card in the row and press Enter
    Then the preview opens
    When I press Escape
    Then the preview closes

  @RS-39 @mobile
  Scenario: The row scrolls sideways and peeks at the next card
    Given I started reading "Dune", "Hyperion" and "Neuromancer"
    Then part of the second card is visible beside the first on a phone
    And the page itself does not scroll sideways
