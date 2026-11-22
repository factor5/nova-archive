Feature: Navigation, keyboard and accessibility
  As any user
  I want to move around the app reliably
  Whether I use touch, mouse or keyboard

  Background:
    Given a fresh browser profile
    And the app is open

  @NV-01 @smoke
  Scenario Outline: Tabs switch pages and update the address
    When I tap the "<tab>" tab
    Then the address ends with "<hash>"
    And the "<tab>" tab is marked current
    And the page shows "<marker>"

    Examples:
      | tab      | hash     | marker                  |
      | Library  | #library | the search box          |
      | My Lists | #lists   | Mission board empty   |
      | About    | #about   | What’s in here        |

  @NV-02
  Scenario: Opening an address goes straight to that page
    When I open the address "#about"
    Then the About page is shown

  @NV-03
  Scenario: Unknown hash falls back to the Library
    When I open the address "#nonsense"
    Then the Library is shown

  @NV-04
  Scenario: The Now reading row is visible on every tab when something is being read
    Given I started reading "Hyperion"
    Then the "Now reading" row shows "Hyperion" on Library, My Lists and About

  @NV-05
  Scenario: The tab bar stays on one line on a phone
    Given a 390 px wide screen
    Then the three tabs fit on one row and none wraps

  @NV-10 @smoke
  Scenario: Back-to-top button
    Given I scrolled down 1000 px
    Then a back-to-top button is visible
    When I tap it
    Then the page is at the top and the button hides

  @NV-11
  Scenario: Back-to-top is hidden near the top
    Then the button is not visible

  @NV-20
  Scenario: Dialogs close with Escape
    Given a book preview dialog is open
    When I press Escape
    Then the dialog closes

  @NV-21
  Scenario: Dialogs close by clicking the backdrop or the close button
    Given a dialog is open
    When I click the backdrop
    Then it closes

  @NV-22
  Scenario: Dialog is labelled and focus moves into it
    When I open a dialog
    Then it has role "dialog" and an accessible name
    And focus is inside it

  @NV-23
  Scenario: Page behind a dialog does not scroll
    Given a dialog is open
    Then scrolling the page behind it is prevented

  @NV-30
  Scenario: Everything is reachable by keyboard
    When I press Tab repeatedly from the top of the page
    Then focus visits the nav, filters, cards' buttons in a logical order
    And every focused element has a visible focus ring

  @NV-31
  Scenario: Enter and Space open a Now reading card
    Given I started reading "Hyperion"
    And the "Now reading" card for "Hyperion" has focus
    When I press Enter
    Then the preview dialog opens

  @NV-32
  Scenario: Icon buttons have names
    Then every button without visible text has an aria-label

  @NV-33
  Scenario: Toasts are announced
    When a toast appears
    Then it sits in a live region with role "status"

  @NV-34
  Scenario: Reduced motion is respected
    Given the device prefers reduced motion
    Then smooth scrolling and transitions are disabled

  @NV-40
  Scenario: Language and viewport
    Then the html element has lang "en"
    And the viewport meta allows zooming

  @NV-41 @mobile
  Scenario Outline: No horizontal overflow on narrow screens
    Given a <width> px wide screen
    When I visit each of Library, My Lists, About, a book page and every dialog
    Then the document is not wider than the screen

    Examples:
      | width |
      | 320   |
      | 360   |
      | 390   |

  @NV-42 @mobile
  Scenario: Touch targets are large enough
    Given a 390 px wide screen
    Then primary buttons are at least 36 px high and compact buttons at least 28 px

  @NV-50
  Scenario: No console errors during normal use
    When I walk through every feature in the other files
    Then the browser console shows no errors or unhandled rejections
