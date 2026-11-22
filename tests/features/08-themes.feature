Feature: Themes
  As a reader
  I want to pick how the app looks
  So that it is comfortable at any time of day

  Background:
    Given a fresh browser profile
    And the app is open on the Library tab

  @TH-01 @smoke
  Scenario: Default is Auto
    Then the theme setting is "Auto"
    And the page follows the device's colour scheme

  @TH-02
  Scenario Outline: Auto follows the device
    Given the device prefers <scheme>
    Then html[data-theme] is "<theme>"

    Examples:
      | scheme | theme |
      | dark   | dark  |
      | light  | paper |

  @TH-03 @smoke
  Scenario Outline: Pick a theme
    When I choose "<label>" in the theme picker
    Then html[data-theme] is "<id>"
    And the browser theme colour is "<meta>"
    And the saved data has theme "<id>"

    Examples:
      | label    | id       | meta    |
      | Nova     | dark     | #04060d |
      | Paper    | paper    | #f3eee1 |
      | Terminal | terminal | #000000 |
      | Dune     | dune     | #1b120b |

  @TH-04
  Scenario: The picker shows the four themes plus Auto
    When I open the theme picker
    Then I see "Auto", "Nova", "Paper", "Terminal" and "Dune", each with a swatch
    And the current one is marked

  @TH-05
  Scenario: Theme survives a reload without a flash
    Given I chose "Terminal"
    When I reload the page
    Then html[data-theme] is "terminal" before the first paint

  @TH-06
  Scenario: Theme syncs across devices
    Given I am signed in and chose "Dune" on device A
    When I sign in on device B
    Then device B uses "dune"

  @TH-07
  Scenario Outline: Every theme renders every view legibly
    Given the theme "<id>" is active
    Then on the Library, My Lists, About and Book pages
    And in the book and rating dialogs
    Then all text has at least 4.5:1 contrast with its background
    And nothing overflows a 390 px screen

    Examples:
      | id       |
      | dark     |
      | paper    |
      | terminal |
      | dune     |

  @TH-08
  Scenario: Switching theme does not lose state
    Given I filtered the Library and opened page 2
    When I switch theme
    Then the filters and page are unchanged

  @TH-09 @manual
  Scenario: Visual check of the themes
    Then each theme looks coherent on a real phone, including the status bar colour
