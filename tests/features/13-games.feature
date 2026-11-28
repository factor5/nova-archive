Feature: Book games
  As a reader
  I want small games based on some books
  So that the app is more playful

  Games are hidden behind "Show games (beta)" on the About page until they are approved.
  Only Dune has a game (Spice Run). Tests start every run with a fixed seed and may speed
  the game up (test hook window.__novaGameTest), so runs are repeatable and short.

  Background:
    Given a fresh browser profile
    And the app is open on the Library tab

  @GM-01 @smoke
  Scenario: Games are hidden by default
    When I open the book page for "Dune"
    Then the book page shows no game

  @GM-02 @smoke
  Scenario: The beta switch shows the game on its book only
    Given games (beta) are switched on
    When I open the book page for "Dune"
    Then the book page shows the game "Spice Run" with a Play button
    When I open the book page for "Hyperion"
    Then the book page shows no game

  @GM-03
  Scenario: The beta switch is kept on this device and can be turned off
    Given games (beta) are switched on
    When I reload the page
    And I open the "About" tab
    Then "Show games (beta)" is on
    When I switch games (beta) off
    And I open the book page for "Dune"
    Then the book page shows no game

  @GM-04 @smoke
  Scenario: Play opens the game screen
    Given games (beta) are switched on
    And I open the book page for "Dune"
    When I tap Play
    Then the address ends with "#play/dune--frank-herbert"
    And the game screen shows "Spice Run" with a play area
    And the game shows its start screen with "Start" and "Back to book"
    When I tap the game button "Start"
    Then the game is running
    And the browser console shows no errors or unhandled rejections

  @GM-05 @smoke
  Scenario: Back to book closes the game
    Given I am playing "Spice Run" from the Dune book page
    When I tap the game button "← Book"
    Then the game screen is closed
    And the address ends with "#book/dune--frank-herbert"
    And the page heading reads "Dune"

  @GM-06
  Scenario: The browser Back button closes the game
    Given I am playing "Spice Run" from the Dune book page
    When I go back in the browser
    Then the game screen is closed
    And the page heading reads "Dune"

  @GM-07
  Scenario: Pause, resume and restart
    Given I am playing "Spice Run" from the Dune book page
    When I tap the game button "Pause"
    Then the game is paused
    And the game does not move while paused
    When I tap the game button "Resume"
    Then the game is running
    When I tap the game button "Pause"
    And I tap the game button "Restart"
    Then the game is running
    And the score is 0

  @GM-08
  Scenario: The game pauses when the app goes to the background
    Given I am playing "Spice Run" from the Dune book page
    When the page becomes hidden
    Then the game is paused

  @GM-09 @desktop
  Scenario: Keyboard moves the player
    Given I am playing "Spice Run" from the Dune book page
    When I hold the right arrow key for a moment
    Then the player has moved right

  @GM-10 @mobile
  Scenario: Dragging moves the player and fast drags make noise
    Given I am playing "Spice Run" from the Dune book page
    When I drag far to the left on the play area and hold
    Then the player has moved left
    And the noise meter is above the worm's hearing level

  @GM-11 @smoke
  Scenario: A run ends and the best score is kept
    Given I am playing "Spice Run" fast from the Dune book page
    When I wait for the run to end
    Then the game over screen shows the score and "Play again"
    When I tap the game button "Back to book"
    Then the game panel shows the best score

  @GM-12
  Scenario: A play address without the beta switch shows only the book
    When I open the address "#play/dune--frank-herbert"
    Then the page heading reads "Dune"
    And the game screen is closed

  @GM-13 @mobile
  Scenario: The game screen fits a phone
    Given I am playing "Spice Run" from the Dune book page
    Then the play area fills the screen below the top bar
    And nothing on the game screen overflows horizontally

  @GM-14 @manual
  Scenario: Playtest on the phone (Motorola Edge 30)
    Given the installed app with games (beta) switched on
    When I play Spice Run a few times in portrait and once in landscape
    Then it starts in about a second and plays smoothly
    And the joystick feels right (no drift, speed easy to control)
    And the noise and worm rule is understandable without explanation
    And a run lasts 2 to 5 minutes
    And pause, going to the background and coming back work
    And "Back to book" is always reachable
    And it works offline after the first play
    And I would play it again
