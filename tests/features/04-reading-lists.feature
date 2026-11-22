Feature: Reading lists
  As a reader
  I want to keep named lists of books
  So that I can plan what to read next

  Background:
    Given a fresh browser profile
    And the app is open on the Library tab

  # ---------- creating ----------

  @RL-01 @smoke
  Scenario: The lists page starts empty
    When I open the "My Lists" tab
    Then a "Mission board empty" message is shown
    And the tab label reads "My Lists" without a count

  @RL-02 @smoke
  Scenario: Create a list
    Given I am on the "My Lists" tab
    When I type "Classics" in the new list box and tap "Create"
    Then the list "Classics" appears in the side list showing "0/0"
    And the list is open and says "This list is empty"
    And the tab label reads "My Lists (1)"

  @RL-03
  Scenario: Create a list with the Enter key
    Given I am on the "My Lists" tab
    When I type "Classics" in the new list box and press Enter
    Then the list "Classics" exists

  @RL-04
  Scenario Outline: Blank list names are rejected
    Given I am on the "My Lists" tab
    When I type "<name>" in the new list box and tap "Create"
    Then no list is created
    And the new list box has focus

    Examples:
      | name |
      |      |
      |      |

  @RL-05
  Scenario: List names are limited to 60 characters and shown as text
    When I create a list named with 80 characters
    Then the saved name has 60 characters
    When I create a list named "<i>Cool</i>"
    Then the name is shown literally as "<i>Cool</i>"

  # ---------- adding books ----------

  @RL-10 @smoke
  Scenario: Add a book to a list from a card
    Given I have a list "Classics"
    When I tap "＋ List" on "Dune"
    Then a dialog "Add to reading list" shows "Classics" unchecked
    When I tap "Classics" in the dialog
    Then "Classics" is checked
    When I tap "Done"
    Then the card for "Dune" shows "＋ List (1)"

  @RL-11
  Scenario: Remove a book by unchecking the list in the dialog
    Given "Dune" is on the list "Classics"
    When I tap "＋ List (1)" on "Dune" and uncheck "Classics"
    Then the card for "Dune" shows "＋ List" without a count

  @RL-12 @smoke
  Scenario: Create a list from the dialog and add the book in one step
    When I tap "＋ List" on "Dune"
    And I type "Fresh list" in the dialog box and tap "Create & add"
    Then the toast "Added to “Fresh list”" is shown
    And the list "Fresh list" holds "Dune"

  @RL-13
  Scenario: One book can be on several lists
    Given I have lists "A" and "B"
    When I add "Dune" to both
    Then the card for "Dune" shows "＋ List (2)"
    And both lists hold "Dune"

  @RL-14
  Scenario: Adding many books at once skips the ones already there
    Given the list "Locus shelf" holds "Hyperion"
    And I selected the "Locus" award filter
    When I use "Add all results to a list" and tap "Locus shelf"
    Then the toast "55 added to “Locus shelf”" is shown
    And the list holds 56 books

  # ---------- viewing ----------

  @RL-20 @smoke
  Scenario: A list shows its books, progress and actions
    Given the list "Classics" holds "Dune", "Hyperion" and "Neuromancer"
    And I marked "Dune" as read
    When I open the "Classics" list
    Then the side list shows "Classics 1/3"
    And the header reads "1 of 3 read" with a progress bar one third full
    And the items are numbered 1, 2, 3 in the order "Dune", "Hyperion", "Neuromancer"
    And "Dune" is struck through and shows "✓ Read"
    And "Hyperion" shows "Mark read", "▶ Start", "↑", "↓" and "✕" buttons

  @RL-21
  Scenario: Reading actions work inside a list
    Given the list "Classics" holds "Dune" and "Hyperion"
    When I open the list and tap "▶ Start" on "Hyperion"
    Then "Hyperion" shows "✓ Finish" and "Stop"
    And the "Now reading" row shows "Hyperion"
    When I tap "✓ Finish" on "Hyperion"
    Then the rating dialog opens

  @RL-22
  Scenario: Titles in a list link to the book page
    Given the list "Classics" holds "Dune"
    When I tap the title "Dune" in the list
    Then the book page for "Dune" is shown

  @RL-23
  Scenario: Switching between lists
    Given I have lists "A" holding "Dune" and "B" holding "Hyperion"
    When I tap "B" in the side list
    Then the list "B" is open and shows "Hyperion"

  # ---------- ordering ----------

  @RL-30 @smoke
  Scenario: Reorder books with the arrows
    Given the list "Classics" holds "Dune", "Hyperion" and "Neuromancer"
    When I tap "↓" on "Dune"
    Then the order is "Hyperion", "Dune", "Neuromancer"
    When I tap "↑" on "Neuromancer"
    Then the order is "Hyperion", "Neuromancer", "Dune"

  @RL-31
  Scenario: The first book cannot move up and the last cannot move down
    Given the list "Classics" holds "Dune" and "Hyperion"
    When I tap "↑" on "Dune"
    And I tap "↓" on "Hyperion"
    Then the order is still "Dune", "Hyperion"

  @RL-32
  Scenario: My order is remembered
    Given I moved "Hyperion" above "Dune" in "Classics"
    When I reload the page and open "Classics"
    Then the order is "Hyperion", "Dune"

  @RL-33
  Scenario Outline: Sort a list without changing my order
    Given the list "Classics" holds "Neuromancer", "Dune" and "Hyperion"
    When I choose "<sort>" in the list's sort menu
    Then the order shown is <shown>
    And the "↑" and "↓" buttons are hidden
    When I choose "My order"
    Then the order is "Neuromancer", "Dune", "Hyperion" again
    And the "↑" and "↓" buttons are back

    Examples:
      | sort         | shown                              |
      | Title A–Z    | "Dune", "Hyperion", "Neuromancer"  |
      | Author A–Z   | "Neuromancer", "Hyperion", "Dune"  |
      | Oldest first | "Dune", "Neuromancer", "Hyperion"  |
      | Newest first | "Hyperion", "Neuromancer", "Dune"  |

  @RL-34
  Scenario: Unread first
    Given the list "Classics" holds "Dune", "Hyperion" and "Neuromancer"
    And I marked "Dune" as read
    When I choose "Unread first" in the list's sort menu
    Then "Dune" is last

  # ---------- managing ----------

  @RL-40
  Scenario: Remove a book from a list
    Given the list "Classics" holds "Dune" and "Hyperion"
    When I tap "✕" on "Dune"
    Then the list holds only "Hyperion"
    And "Dune" is still in the library

  @RL-41 @smoke
  Scenario: Rename a list
    Given I have a list "Classics"
    When I change its name to "Favourites" and leave the field
    Then the side list shows "Favourites"
    And the saved data has the list name "Favourites"

  @RL-42
  Scenario: A blank name is not accepted when renaming
    Given I have a list "Classics"
    When I clear its name and leave the field
    Then the name goes back to "Classics"

  @RL-43 @smoke
  Scenario: Delete a list needs two taps
    Given I have a list "Classics" holding "Dune"
    When I tap "Delete list"
    Then the button reads "Click again to confirm"
    And the list still exists
    When I tap it again
    Then the toast "List deleted" is shown
    And the list is gone
    And "Dune" is still in the library

  @RL-44
  Scenario: The delete confirmation expires
    Given I tapped "Delete list" once
    When 3 seconds pass
    Then the button reads "Delete list" again

  @RL-45
  Scenario: Copy a list as text
    Given the list "Classics" holds "Dune" (read) and "Hyperion"
    When I tap "Copy as text"
    Then the toast "List copied" is shown
    And the clipboard holds these lines:
      """
      Classics
      1. Dune — Frank Herbert [read]
      2. Hyperion — Dan Simmons
      """

  @RL-46
  Scenario: Copy falls back to a dialog when the clipboard is unavailable
    Given the clipboard cannot be written
    When I tap "Copy as text"
    Then a dialog "Copy list" shows the same text in a selectable box

  @RL-47
  Scenario: Lists survive a reload
    Given I have a list "Classics" holding "Dune"
    When I reload the page
    Then the tab label reads "My Lists (1)"
    And the list still holds "Dune"

  @RL-48 @mobile
  Scenario: The lists page fits a phone screen
    Given a list with a long name and several books with long titles
    Then nothing overflows the screen horizontally
    And each item's buttons wrap below its text

  @RL-49
  Scenario: A book that no longer exists is skipped quietly
    Given the saved data has a list that holds an unknown book id
    When I open the list
    Then the unknown entry is not shown and the page does not fail
