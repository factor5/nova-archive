Feature: Persistence and cloud sync
  As a reader
  I want my data kept on the device and synced when I sign in
  So that nothing is lost and all my devices agree
  (Firebase is replaced by the fake in tests/support/mocks)

  Background:
    Given a fresh browser profile
    And the app is open

  # ---------- local ----------

  @SY-01 @smoke
  Scenario: Data is stored locally without signing in
    Given I am signed out
    When I mark "Dune" read and reload
    Then "Dune" is still read
    And the status shows "Saved in this browser only"

  @SY-02
  Scenario: Corrupt local data does not break the app
    Given localStorage "nova-archive-v1" contains "{not json"
    When I open the app
    Then the Library loads with nothing read

  @SY-03
  Scenario: Unknown fields are ignored and defaults applied
    Given the stored data is {"v":2,"read":["dune--frank-herbert"]}
    When I open the app
    Then "Dune" is read and no lists, ratings or notes exist

  @SY-04
  Scenario: Unknown ids in stored data are kept but not shown
    Given the stored data marks "gone--nobody" as read
    When I open the app
    Then the Library count is unchanged and no error appears

  # ---------- signing in ----------

  @SY-10 @smoke @firebase-mock
  Scenario: Sign in with Google
    When I tap the sign-in icon button
    Then the button becomes a sign-out icon
    And the status shows "Cloud synced"

  @SY-11 @firebase-mock
  Scenario: Local data is uploaded when the cloud is empty
    Given I marked "Dune" read while signed out
    And the cloud has no document for me
    When I sign in
    Then the cloud document holds "dune--frank-herbert" as read

  @SY-12 @firebase-mock
  Scenario: Cloud data is loaded when local is empty
    Given the cloud document marks "Hyperion" read
    When I sign in on a fresh device
    Then "Hyperion" is read

  @SY-13 @firebase-mock
  Scenario Outline: Newer data wins
    Given local data updated at <local> and cloud data updated at <cloud>
    When I sign in
    Then the <winner> data is used on both sides

    Examples:
      | local | cloud | winner |
      | 2000  | 1000  | local  |
      | 1000  | 2000  | cloud  |

  @SY-14 @firebase-mock
  Scenario: Every kind of data is synced
    Given I am signed in
    When I read, rate, note, start, list, add a custom book and pick a theme
    Then the cloud document contains read, meta, reading, lists, custom and theme with v 2

  @SY-15 @firebase-mock
  Scenario: Changes are batched
    Given I am signed in
    When I make 5 changes within half a second
    Then exactly one cloud write happens within about a second

  @SY-16 @firebase-mock
  Scenario: A change from another device arrives
    Given I am signed in
    When the cloud document changes on another device
    Then the app shows the new data without a reload

  @SY-17 @firebase-mock
  Scenario: Sign out keeps local data
    Given I am signed in with "Dune" read
    When I tap sign out
    Then "Dune" is still read
    And the status shows "Sign in to sync"

  @SY-18 @firebase-mock
  Scenario: Two accounts on one device do not mix
    Given account A is signed in with "Dune" read
    When I sign out and sign in as account B whose cloud is empty
    Then account B's cloud document does not contain "Dune"

  # ---------- failures ----------

  @SY-20 @firebase-mock
  Scenario: A failing write is reported and retried
    Given I am signed in
    And the next cloud write fails
    When I mark "Dune" read
    Then the status shows "Sync problem – kept in this browser"
    And the data is still saved locally
    When I make another change
    Then the write succeeds and the status shows "Cloud synced"

  @SY-21 @firebase-mock
  Scenario: Offline edits sync later
    Given I am signed in and the network is offline
    When I mark "Dune" read
    Then the status shows "Offline – will sync when connected" and the data is local
    When the network returns
    Then the cloud document has "Dune"

  @SY-22 @firebase-mock
  Scenario: Sign-in cancelled
    Given the sign-in popup is closed by the user
    Then the app stays signed out with no error message

  @SY-23
  Scenario: Firebase SDK cannot be loaded
    Given the Firebase SDK request is blocked
    When I open the app
    Then the app works in local-only mode

  # ---------- status display ----------

  @SY-25 @mobile @firebase-mock
  Scenario: Compact header on a phone
    Given a 390 px wide screen
    Then the sign-in control is an icon button
    And the sync status is an icon with a tooltip
    And the nav tabs stay on one line

  # ---------- manual ----------

  @SY-30 @manual
  Scenario: Firestore rules protect each user's document
    Given the published Firestore rules
    Then a signed-in user can read and write only users/<own uid>
    And a signed-out visitor can read and write nothing
